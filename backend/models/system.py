from sqlalchemy import Column, String, Integer, Float, Numeric, Date, ForeignKey, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    full_name = Column(String(128), nullable=False)
    role = Column(String(32), default="manager", nullable=False)  # admin, manager, analyst
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    business_profiles = relationship("BusinessProfile", back_populates="user", cascade="all, delete-orphan")
    analysis_sessions = relationship("AnalysisSession", back_populates="user", cascade="all, delete-orphan")
    generated_reports = relationship("GeneratedReport", back_populates="user", cascade="all, delete-orphan")
    chat_conversations = relationship("ChatConversation", back_populates="user", cascade="all, delete-orphan")

class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_name = Column(String(128), nullable=False, default="Retail Enterprise Co.")
    industry = Column(String(64), nullable=False, default="Retail")
    team_size = Column(String(32), default="50-100")
    target_margin = Column(Numeric(5, 2), default=25.00)
    business_goals = Column(Text, default="Maximize gross profit margin, reduce return leakage, and optimize warehouse inventory turnover.")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="business_profiles")

class UploadedDataset(Base):
    __tablename__ = "uploaded_datasets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    filename = Column(String(256), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    total_records = Column(Integer, default=0)
    sheet_details = Column(JSON, default=dict)
    status = Column(String(32), default="Completed")  # Processing, Completed, Failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dataset_id = Column(Integer, ForeignKey("uploaded_datasets.id"), nullable=True)
    status = Column(String(32), default="Pending")  # Pending, Running, Completed, Verified, Failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    execution_duration_sec = Column(Float, default=0.0)
    executive_summary = Column(Text, nullable=True)
    consolidated_plan = Column(JSON, default=dict)
    is_verified = Column(Boolean, default=False)
    verification_scorecard = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="analysis_sessions")
    agent_logs = relationship("AgentLog", back_populates="session", cascade="all, delete-orphan")
    recommendations = relationship("StrategicRecommendation", back_populates="session", cascade="all, delete-orphan")

class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("analysis_sessions.id"), nullable=False)
    agent_name = Column(String(64), nullable=False)  # Data Analyst, Marketing, Finance, Operations, Strategy, Verification
    agent_role = Column(String(128), nullable=False)
    task_name = Column(String(128), nullable=False)
    status = Column(String(32), default="Running")  # Running, Completed, Failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    execution_duration_sec = Column(Float, default=0.0)
    output_text = Column(Text, nullable=True)
    structured_data = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("AnalysisSession", back_populates="agent_logs")

class StrategicRecommendation(Base):
    __tablename__ = "strategic_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("analysis_sessions.id"), nullable=False)
    title = Column(String(256), nullable=False)
    category = Column(String(64), nullable=False)  # Marketing, Finance, Operations, Strategy
    description = Column(Text, nullable=False)
    expected_roi = Column(String(128), nullable=True)
    risk_level = Column(String(32), default="Medium")  # Low, Medium, High
    supporting_evidence = Column(JSON, default=dict)
    status = Column(String(32), default="Pending")  # Pending, Approved, Rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("AnalysisSession", back_populates="recommendations")
    approval_request = relationship("ApprovalRequest", back_populates="recommendation", uselist=False, cascade="all, delete-orphan")

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("strategic_recommendations.id"), nullable=False)
    requested_by_agent = Column(String(64), default="Strategy Agent")
    reviewed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    decision = Column(String(32), default="Pending")  # Pending, Approved, Rejected
    manager_comments = Column(Text, nullable=True)
    decision_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    recommendation = relationship("StrategicRecommendation", back_populates="approval_request")

class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("analysis_sessions.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type = Column(String(64), nullable=False)  # Consolidated, DataAnalyst, Marketing, Finance, Operations, Strategy, Verification
    title = Column(String(256), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="generated_reports")

class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(256), nullable=False, default="Retail Business Inquiry")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"), nullable=False)
    sender = Column(String(16), nullable=False)  # user, assistant
    message = Column(Text, nullable=False)
    grounding_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("ChatConversation", back_populates="messages")
