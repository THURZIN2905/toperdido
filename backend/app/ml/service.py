import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from typing import Dict, List, Tuple
from datetime import datetime

class MLService:
    def __init__(self, model_path: str = "./models/"):
        self.model_path = model_path
        self.scaler = None
        self.kmeans_model = None
        self.rf_model = None
        self.feature_names = []
        self.course_mapping = {
            0: "Tecnologia da Informação",
            1: "Enfermagem", 
            2: "Logística",
            3: "Administração",
            4: "Estética"
        }
        self.load_models()
    
    def load_models(self):
        """Carrega modelos treinados"""
        try:
            if os.path.exists(os.path.join(self.model_path, "scaler.joblib")):
                self.scaler = joblib.load(os.path.join(self.model_path, "scaler.joblib"))
            
            if os.path.exists(os.path.join(self.model_path, "kmeans_model.joblib")):
                self.kmeans_model = joblib.load(os.path.join(self.model_path, "kmeans_model.joblib"))
            
            if os.path.exists(os.path.join(self.model_path, "rf_model.joblib")):
                self.rf_model = joblib.load(os.path.join(self.model_path, "rf_model.joblib"))
            
            if os.path.exists(os.path.join(self.model_path, "feature_names.joblib")):
                self.feature_names = joblib.load(os.path.join(self.model_path, "feature_names.joblib"))
                
        except Exception as e:
            print(f"Erro ao carregar modelos: {e}")
            self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Inicializa modelos padrão se não existirem"""
        # Criar dados sintéticos para inicialização
        np.random.seed(42)
        n_samples = 1000
        n_features = 20
        
        # Gerar dados sintéticos
        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, 5, n_samples)
        
        # Treinar modelos básicos
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.kmeans_model = KMeans(n_clusters=5, random_state=42)
        self.kmeans_model.fit(X_scaled)
        
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.rf_model.fit(X_scaled, y)
        
        self.feature_names = [f"feature_{i}" for i in range(n_features)]
        
        # Salvar modelos
        self.save_models()
    
    def save_models(self):
        """Salva modelos treinados"""
        os.makedirs(self.model_path, exist_ok=True)
        
        if self.scaler:
            joblib.dump(self.scaler, os.path.join(self.model_path, "scaler.joblib"))
        
        if self.kmeans_model:
            joblib.dump(self.kmeans_model, os.path.join(self.model_path, "kmeans_model.joblib"))
        
        if self.rf_model:
            joblib.dump(self.rf_model, os.path.join(self.model_path, "rf_model.joblib"))
        
        if self.feature_names:
            joblib.dump(self.feature_names, os.path.join(self.model_path, "feature_names.joblib"))
    
    def preprocess_responses(self, responses: List[Dict]) -> np.ndarray:
        """Preprocessa respostas do questionário para o modelo"""
        # Converter respostas em features numéricas
        features = []
        
        for response in responses:
            # Extrair features das respostas
            # Isso seria customizado baseado na estrutura real das perguntas
            question_id = response.get("question_id", 0)
            option_id = response.get("selected_option_id", 0)
            response_time = response.get("response_time_ms", 0)
            
            # Criar features básicas
            features.extend([question_id, option_id, response_time])
        
        # Preencher ou truncar para ter o número correto de features
        target_length = len(self.feature_names) if self.feature_names else 20
        
        if len(features) < target_length:
            features.extend([0] * (target_length - len(features)))
        elif len(features) > target_length:
            features = features[:target_length]
        
        return np.array(features).reshape(1, -1)
    
    def calculate_weighted_scores(self, responses: List[Dict]) -> Dict[str, float]:
        """Calcula pontuações baseadas nos pesos das opções"""
        scores = {
            "ti": 0.0,
            "enfermagem": 0.0,
            "logistica": 0.0,
            "administracao": 0.0,
            "estetica": 0.0
        }
        
        total_weight = 0
        
        for response in responses:
            # Usar pesos reais se disponíveis
            weights = response.get("weights", {
                "ti": 5.0,
                "enfermagem": 5.0,
                "logistica": 5.0,
                "administracao": 5.0,
                "estetica": 5.0
            })
            
            for course in scores:
                weight_key = f"weight_{course}" if course != "ti" else "weight_ti"
                scores[course] += weights.get(weight_key, weights.get(course, 5.0))
            
            total_weight += sum(weights.values()) if isinstance(weights, dict) else 25.0
        
        # Normalizar pontuações para 0-100
        if total_weight > 0:
            for course in scores:
                scores[course] = (scores[course] / total_weight) * 100
        
        return scores
    
    def classify_responses(self, responses: List[Dict]) -> Dict:
        """Classifica respostas e retorna recomendação"""
        start_time = datetime.now()
        
        try:
            # Calcular pontuações baseadas em pesos
            weighted_scores = self.calculate_weighted_scores(responses)
            
            # Se modelos ML estão disponíveis, usar também
            if self.scaler and self.rf_model:
                features = self.preprocess_responses(responses)
                features_scaled = self.scaler.transform(features)
                
                # Predição do modelo
                ml_prediction = self.rf_model.predict(features_scaled)[0]
                ml_probabilities = self.rf_model.predict_proba(features_scaled)[0]
                
                # Combinar pontuações ponderadas com ML
                ml_course = self.course_mapping.get(ml_prediction, "Tecnologia da Informação")
                ml_confidence = max(ml_probabilities)
                
                # Ajustar pontuações baseadas na predição ML
                if ml_course == "Tecnologia da Informação":
                    weighted_scores["ti"] *= 1.2
                elif ml_course == "Enfermagem":
                    weighted_scores["enfermagem"] *= 1.2
                elif ml_course == "Logística":
                    weighted_scores["logistica"] *= 1.2
                elif ml_course == "Administração":
                    weighted_scores["administracao"] *= 1.2
                elif ml_course == "Estética":
                    weighted_scores["estetica"] *= 1.2
            
            # Determinar curso recomendado
            recommended_course_key = max(weighted_scores, key=weighted_scores.get)
            course_names = {
                "ti": "Tecnologia da Informação",
                "enfermagem": "Enfermagem",
                "logistica": "Logística", 
                "administracao": "Administração",
                "estetica": "Estética"
            }
            
            recommended_course = course_names[recommended_course_key]
            
            # Calcular confiança baseada na diferença entre o maior e segundo maior score
            sorted_scores = sorted(weighted_scores.values(), reverse=True)
            confidence = (sorted_scores[0] - sorted_scores[1]) / 100 if len(sorted_scores) > 1 else 0.8
            confidence = min(max(confidence, 0.1), 1.0)  # Limitar entre 0.1 e 1.0
            
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return {
                "scores": {
                    "ti": weighted_scores["ti"],
                    "enfermagem": weighted_scores["enfermagem"],
                    "logistica": weighted_scores["logistica"],
                    "administracao": weighted_scores["administracao"],
                    "estetica": weighted_scores["estetica"]
                },
                "recommended_course": recommended_course,
                "confidence_score": confidence,
                "processing_time_ms": processing_time,
                "model_version": "1.0.0"
            }
            
        except Exception as e:
            print(f"Erro na classificação: {e}")
            # Retornar resultado padrão em caso de erro
            return {
                "scores": {
                    "ti": 20.0,
                    "enfermagem": 20.0,
                    "logistica": 20.0,
                    "administracao": 20.0,
                    "estetica": 20.0
                },
                "recommended_course": "Tecnologia da Informação",
                "confidence_score": 0.5,
                "processing_time_ms": 100,
                "model_version": "1.0.0"
            }
    
    def retrain_model(self, training_data: pd.DataFrame):
        """Retreina modelo com novos dados"""
        try:
            # Preparar dados
            X = training_data.drop(['target'], axis=1)
            y = training_data['target']
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Treinar scaler
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Treinar modelos
            self.kmeans_model = KMeans(n_clusters=5, random_state=42)
            self.kmeans_model.fit(X_train_scaled)
            
            self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.rf_model.fit(X_train_scaled, y_train)
            
            # Avaliar modelo
            y_pred = self.rf_model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Salvar modelos
            self.save_models()
            
            return {
                "success": True,
                "accuracy": accuracy,
                "message": "Modelo retreinado com sucesso"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao retreinar modelo"
            }
    
    def get_model_info(self) -> Dict:
        """Retorna informações sobre o modelo atual"""
        return {
            "version": "1.0.0",
            "last_trained": datetime.now(),
            "accuracy": 0.85,  # Placeholder
            "total_samples": 1000,  # Placeholder
            "features_count": len(self.feature_names) if self.feature_names else 0,
            "model_type": "Random Forest + K-Means"
        }

