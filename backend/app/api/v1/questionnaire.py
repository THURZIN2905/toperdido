from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas import (
    QuestionResponse, QuestionnaireSubmission, RecommendationResultResponse,
    EmailResultRequest
)
from app.models import Question, QuestionOption, QuestionnaireResponse, RecommendationResult, User, QuestionType
from app.api.v1.auth import get_current_user_optional
from app.ml.service import MLService
from app.utils.auth import generate_session_id
import time

router = APIRouter(prefix="/questionnaire", tags=["questionnaire"])

# Instância do serviço ML
ml_service = MLService()

@router.get("/questions", response_model=List[QuestionResponse])
async def get_active_questions(db: Session = Depends(get_db)):
    """Retorna todas as perguntas ativas ordenadas"""
    try:
        questions = db.query(Question).filter(
            Question.is_active == True
        ).order_by(Question.order).all()
        
        if not questions:
            # Criar perguntas de exemplo se não existirem
            try:
                create_sample_questions(db)
                questions = db.query(Question).filter(
                    Question.is_active == True
                ).order_by(Question.order).all()
            except Exception as create_error:
                print(f"Erro ao criar perguntas de exemplo: {create_error}")
                return []
        
        return questions
    except Exception as e:
        print(f"Erro ao buscar perguntas: {e}")
        return []

@router.post("/submit", response_model=RecommendationResultResponse)
async def submit_questionnaire(
    submission: QuestionnaireSubmission,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Submete respostas do questionário e retorna recomendação"""
    start_time = time.time()
    
    try:
        # Salvar respostas no banco
        for response_data in submission.responses:
            # Verificar se pergunta e opção existem
            question = db.query(Question).filter(Question.id == response_data.question_id).first()
            if not question:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Pergunta {response_data.question_id} não encontrada"
                )
            
            option = db.query(QuestionOption).filter(
                QuestionOption.id == response_data.selected_option_id
            ).first()
            if not option:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Opção {response_data.selected_option_id} não encontrada"
                )
            
            # Criar resposta
            db_response = QuestionnaireResponse(
                user_id=current_user.id if current_user else None,
                session_id=submission.session_id,
                question_id=response_data.question_id,
                selected_option_id=response_data.selected_option_id,
                response_time_ms=response_data.response_time_ms
            )
            db.add(db_response)
        
        db.commit()
        
        # Buscar respostas com pesos para classificação
        responses_with_weights = []
        for response_data in submission.responses:
            option = db.query(QuestionOption).filter(
                QuestionOption.id == response_data.selected_option_id
            ).first()
            
            responses_with_weights.append({
                "question_id": response_data.question_id,
                "selected_option_id": response_data.selected_option_id,
                "response_time_ms": response_data.response_time_ms,
                "weights": {
                    "ti": option.weight_ti,
                    "enfermagem": option.weight_enfermagem,
                    "logistica": option.weight_logistica,
                    "administracao": option.weight_administracao,
                    "estetica": option.weight_estetica
                }
            })
        
        # Classificar usando ML
        classification_result = ml_service.classify_responses(responses_with_weights)
        
        # Salvar resultado
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        db_result = RecommendationResult(
            user_id=current_user.id if current_user else None,
            session_id=submission.session_id,
            score_ti=classification_result["scores"]["ti"],
            score_enfermagem=classification_result["scores"]["enfermagem"],
            score_logistica=classification_result["scores"]["logistica"],
            score_administracao=classification_result["scores"]["administracao"],
            score_estetica=classification_result["scores"]["estetica"],
            recommended_course=classification_result["recommended_course"],
            confidence_score=classification_result["confidence_score"],
            model_version=classification_result["model_version"],
            processing_time_ms=processing_time_ms
        )
        
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        
        return db_result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar questionário: {str(e)}"
        )

@router.get("/result/{session_id}", response_model=RecommendationResultResponse)
async def get_result(session_id: str, db: Session = Depends(get_db)):
    """Retorna resultado de uma sessão específica"""
    result = db.query(RecommendationResult).filter(
        RecommendationResult.session_id == session_id
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultado não encontrado"
        )
    
    return result

@router.post("/result/{session_id}/email")
async def email_result(
    session_id: str,
    email_data: EmailResultRequest,
    db: Session = Depends(get_db)
):
    """Envia resultado por email"""
    # Buscar resultado
    result = db.query(RecommendationResult).filter(
        RecommendationResult.session_id == session_id
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultado não encontrado"
        )
    
    try:
        # TODO: Implementar envio de email
        # Por enquanto, simular sucesso
        return {
            "message": "Email enviado com sucesso",
            "email": email_data.email,
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao enviar email: {str(e)}"
        )

def create_sample_questions(db: Session):
    """Cria perguntas de exemplo para demonstração"""
    sample_questions = [
        {
            "text": "Qual área de conhecimento mais desperta seu interesse?",
            "question_type": QuestionType.MULTIPLE_CHOICE,
            "category": "Interesse Acadêmico",
            "order": 1,
            "options": [
                {"text": "Tecnologia e Computação", "value": "tech", "order": 1, "weight_ti": 10, "weight_enfermagem": 2, "weight_logistica": 3, "weight_administracao": 4, "weight_estetica": 1},
                {"text": "Ciências da Saúde", "value": "health", "order": 2, "weight_ti": 2, "weight_enfermagem": 10, "weight_logistica": 1, "weight_administracao": 3, "weight_estetica": 4},
                {"text": "Gestão e Negócios", "value": "business", "order": 3, "weight_ti": 3, "weight_enfermagem": 2, "weight_logistica": 8, "weight_administracao": 10, "weight_estetica": 2},
                {"text": "Arte e Beleza", "value": "beauty", "order": 4, "weight_ti": 1, "weight_enfermagem": 3, "weight_logistica": 2, "weight_administracao": 2, "weight_estetica": 10},
                {"text": "Logística e Operações", "value": "logistics", "order": 5, "weight_ti": 4, "weight_enfermagem": 1, "weight_logistica": 10, "weight_administracao": 6, "weight_estetica": 1}
            ]
        },
        {
            "text": "Como você prefere trabalhar?",
            "question_type": QuestionType.MULTIPLE_CHOICE, 
            "category": "Estilo de Trabalho",
            "order": 2,
            "options": [
                {"text": "Sozinho, focado em projetos técnicos", "value": "solo_tech", "order": 1, "weight_ti": 9, "weight_enfermagem": 3, "weight_logistica": 4, "weight_administracao": 2, "weight_estetica": 5},
                {"text": "Em equipe, cuidando de pessoas", "value": "team_care", "order": 2, "weight_ti": 3, "weight_enfermagem": 9, "weight_logistica": 5, "weight_administracao": 7, "weight_estetica": 8},
                {"text": "Coordenando processos e pessoas", "value": "coordination", "order": 3, "weight_ti": 4, "weight_enfermagem": 5, "weight_logistica": 9, "weight_administracao": 9, "weight_estetica": 3},
                {"text": "Criando e transformando", "value": "creative", "order": 4, "weight_ti": 5, "weight_enfermagem": 4, "weight_logistica": 2, "weight_administracao": 3, "weight_estetica": 9}
            ]
        },
        {
            "text": "Qual ambiente de trabalho você prefere?",
            "question_type": QuestionType.MULTIPLE_CHOICE,
            "category": "Ambiente de Trabalho", 
            "order": 3,
            "options": [
                {"text": "Escritório com computadores", "value": "office_tech", "order": 1, "weight_ti": 9, "weight_enfermagem": 2, "weight_logistica": 6, "weight_administracao": 8, "weight_estetica": 3},
                {"text": "Hospital ou clínica", "value": "healthcare", "order": 2, "weight_ti": 1, "weight_enfermagem": 10, "weight_logistica": 1, "weight_administracao": 2, "weight_estetica": 3},
                {"text": "Armazém ou centro de distribuição", "value": "warehouse", "order": 3, "weight_ti": 3, "weight_enfermagem": 2, "weight_logistica": 10, "weight_administracao": 4, "weight_estetica": 1},
                {"text": "Salão de beleza ou spa", "value": "salon", "order": 4, "weight_ti": 1, "weight_enfermagem": 3, "weight_logistica": 1, "weight_administracao": 2, "weight_estetica": 10}
            ]
        }
    ]
    
    for q_data in sample_questions:
        # Verificar se pergunta já existe
        existing = db.query(Question).filter(Question.text == q_data["text"]).first()
        if existing:
            continue
            
        question = Question(
            text=q_data["text"],
            question_type=q_data["question_type"],
            category=q_data["category"],
            order=q_data["order"]
        )
        db.add(question)
        db.flush()  # Para obter o ID
        
        for opt_data in q_data["options"]:
            option = QuestionOption(
                question_id=question.id,
                text=opt_data["text"],
                value=opt_data["value"],
                order=opt_data["order"],
                weight_ti=opt_data["weight_ti"],
                weight_enfermagem=opt_data["weight_enfermagem"],
                weight_logistica=opt_data["weight_logistica"],
                weight_administracao=opt_data["weight_administracao"],
                weight_estetica=opt_data["weight_estetica"]
            )
            db.add(option)
    
    db.commit()

