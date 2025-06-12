from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.schemas import (
    QuestionResponse, QuestionCreate, QuestionUpdate, DashboardStats,
    UserResponse
)
from app.models import (
    Question, QuestionOption, QuestionnaireResponse, RecommendationResult, 
    User, UserRole
)
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["administration"])

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency para verificar se usuário é admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem acessar este recurso."
        )
    return current_user

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Retorna estatísticas do dashboard administrativo"""
    
    # Total de respostas
    total_responses = db.query(QuestionnaireResponse).count()
    
    # Total de usuários
    total_users = db.query(User).count()
    
    # Respostas hoje
    today = datetime.utcnow().date()
    responses_today = db.query(QuestionnaireResponse).filter(
        func.date(QuestionnaireResponse.created_at) == today
    ).count()
    
    # Curso mais recomendado
    most_recommended = db.query(
        RecommendationResult.recommended_course,
        func.count(RecommendationResult.recommended_course).label('count')
    ).group_by(
        RecommendationResult.recommended_course
    ).order_by(desc('count')).first()
    
    most_recommended_course = most_recommended[0] if most_recommended else "Nenhum"
    
    # Confiança média
    avg_confidence = db.query(
        func.avg(RecommendationResult.confidence_score)
    ).scalar() or 0.0
    
    return DashboardStats(
        total_responses=total_responses,
        total_users=total_users,
        responses_today=responses_today,
        most_recommended_course=most_recommended_course,
        average_confidence=round(avg_confidence, 2)
    )

@router.get("/questions", response_model=List[QuestionResponse])
async def get_all_questions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Lista todas as perguntas (admin)"""
    questions = db.query(Question).offset(skip).limit(limit).all()
    return questions

@router.post("/questions", response_model=QuestionResponse)
async def create_question(
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Cria nova pergunta"""
    try:
        # Criar pergunta
        db_question = Question(
            text=question_data.text,
            question_type=question_data.question_type,
            category=question_data.category,
            order=question_data.order,
            is_active=question_data.is_active
        )
        db.add(db_question)
        db.flush()  # Para obter o ID
        
        # Criar opções
        for option_data in question_data.options:
            db_option = QuestionOption(
                question_id=db_question.id,
                text=option_data.text,
                value=option_data.value,
                order=option_data.order,
                weight_ti=option_data.weight_ti,
                weight_enfermagem=option_data.weight_enfermagem,
                weight_logistica=option_data.weight_logistica,
                weight_administracao=option_data.weight_administracao,
                weight_estetica=option_data.weight_estetica
            )
            db.add(db_option)
        
        db.commit()
        db.refresh(db_question)
        return db_question
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar pergunta: {str(e)}"
        )

@router.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Atualiza pergunta existente"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pergunta não encontrada"
        )
    
    try:
        # Atualizar campos da pergunta
        if question_data.text is not None:
            question.text = question_data.text
        if question_data.question_type is not None:
            question.question_type = question_data.question_type
        if question_data.category is not None:
            question.category = question_data.category
        if question_data.order is not None:
            question.order = question_data.order
        if question_data.is_active is not None:
            question.is_active = question_data.is_active
        
        # Se novas opções foram fornecidas, substituir as existentes
        if question_data.options is not None:
            # Remover opções existentes
            db.query(QuestionOption).filter(
                QuestionOption.question_id == question_id
            ).delete()
            
            # Criar novas opções
            for option_data in question_data.options:
                db_option = QuestionOption(
                    question_id=question.id,
                    text=option_data.text,
                    value=option_data.value,
                    order=option_data.order,
                    weight_ti=option_data.weight_ti,
                    weight_enfermagem=option_data.weight_enfermagem,
                    weight_logistica=option_data.weight_logistica,
                    weight_administracao=option_data.weight_administracao,
                    weight_estetica=option_data.weight_estetica
                )
                db.add(db_option)
        
        db.commit()
        db.refresh(question)
        return question
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar pergunta: {str(e)}"
        )

@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Remove pergunta"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pergunta não encontrada"
        )
    
    try:
        # Verificar se há respostas associadas
        responses_count = db.query(QuestionnaireResponse).filter(
            QuestionnaireResponse.question_id == question_id
        ).count()
        
        if responses_count > 0:
            # Não deletar, apenas desativar
            question.is_active = False
            db.commit()
            return {"message": f"Pergunta desativada (havia {responses_count} respostas associadas)"}
        else:
            # Deletar pergunta e opções (cascade)
            db.delete(question)
            db.commit()
            return {"message": "Pergunta removida com sucesso"}
            
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover pergunta: {str(e)}"
        )

@router.get("/responses")
async def get_responses_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    course: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Retorna analytics de respostas com filtros"""
    
    query = db.query(RecommendationResult)
    
    # Aplicar filtros
    if start_date:
        query = query.filter(RecommendationResult.created_at >= start_date)
    if end_date:
        query = query.filter(RecommendationResult.created_at <= end_date)
    if course:
        query = query.filter(RecommendationResult.recommended_course == course)
    
    results = query.all()
    
    # Calcular estatísticas
    total_results = len(results)
    if total_results == 0:
        return {
            "total_results": 0,
            "course_distribution": {},
            "average_confidence": 0,
            "average_processing_time": 0
        }
    
    # Distribuição por curso
    course_distribution = {}
    total_confidence = 0
    total_processing_time = 0
    
    for result in results:
        course = result.recommended_course
        course_distribution[course] = course_distribution.get(course, 0) + 1
        total_confidence += result.confidence_score
        total_processing_time += result.processing_time_ms
    
    return {
        "total_results": total_results,
        "course_distribution": course_distribution,
        "average_confidence": round(total_confidence / total_results, 2),
        "average_processing_time": round(total_processing_time / total_results, 2),
        "results": [
            {
                "id": r.id,
                "session_id": r.session_id,
                "recommended_course": r.recommended_course,
                "confidence_score": r.confidence_score,
                "created_at": r.created_at
            } for r in results
        ]
    }

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Lista todos os usuários"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: UserRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Atualiza role de um usuário"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    user.role = new_role
    db.commit()
    
    return {"message": f"Role do usuário {user.email} atualizada para {new_role.value}"}

@router.put("/users/{user_id}/status")
async def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Ativa/desativa um usuário"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    user.is_active = not user.is_active
    db.commit()
    
    status_text = "ativado" if user.is_active else "desativado"
    return {"message": f"Usuário {user.email} {status_text}"}

@router.get("/export/{format}")
async def export_data(
    format: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Exporta dados em formato especificado (CSV, Excel, Word)"""
    
    if format not in ["csv", "excel", "word"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato deve ser: csv, excel ou word"
        )
    
    # TODO: Implementar exportação real
    # Por enquanto, retornar placeholder
    return {
        "message": f"Exportação em formato {format} será implementada",
        "format": format,
        "start_date": start_date,
        "end_date": end_date
    }

