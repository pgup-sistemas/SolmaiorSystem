"""Popula o banco de dados com dados de demonstração completos.

Execute com:

    ./venv/bin/python scripts/populate_demo_data.py

O script é idempotente: ele verifica se cada registro já existe antes de criar.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app, db
from app.models import (
    Document,
    Enrollment,
    LessonSchedule,
    NewsPost,
    Payment,
    Recital,
    RecitalParticipant,
    RecitalPerformance,
    Room,
    ScheduledNotification,
    Student,
    Teacher,
    TrialLesson,
    User,
)

app = create_app()

DATA_DIR = Path(__file__).resolve().parents[1] / "attached_assets"
DATA_DIR.mkdir(exist_ok=True)

PASSWORD_DEFAULT = "SolMaior@2025"


def get_or_create_user(email: str, role: str, **kwargs) -> User:
    user = User.query.filter_by(email=email).first()
    if user:
        needs_commit = False
        for key, value in kwargs.items():
            if hasattr(user, key) and getattr(user, key) != value:
                setattr(user, key, value)
                needs_commit = True
        if not user.check_password(PASSWORD_DEFAULT):
            user.set_password(PASSWORD_DEFAULT)
            needs_commit = True
        if needs_commit:
            db.session.add(user)
        return user

    user = User(
        email=email,
        role=role,
        is_active=True,
        **kwargs,
    )
    user.set_password(PASSWORD_DEFAULT)
    db.session.add(user)
    db.session.flush()
    return user


def ensure_teacher(user: User, instrument: str, specialization: str) -> Teacher:
    teacher = Teacher.query.filter_by(user_id=user.id).first()
    if teacher:
        teacher.instrument = instrument
        teacher.specialization = specialization
        db.session.add(teacher)
        return teacher

    teacher = Teacher(
        user_id=user.id,
        instrument=instrument,
        specialization=specialization,
        bio=f"Professor(a) com especialização em {specialization}.",
        hourly_rate=180.0,
    )
    db.session.add(teacher)
    db.session.flush()
    return teacher


def ensure_student(user: User, instrument: str, level: str, **extra) -> Student:
    student = Student.query.filter_by(user_id=user.id).first()
    if student:
        student.instrument = instrument
        student.level = level
        for key, value in extra.items():
            if hasattr(student, key):
                setattr(student, key, value)
        db.session.add(student)
        return student

    student = Student(
        user_id=user.id,
        instrument=instrument,
        level=level,
        **extra,
    )
    db.session.add(student)
    db.session.flush()
    return student


def main() -> None:
    with app.app_context():
        db.session.execute(db.text("PRAGMA foreign_keys=ON"))

        # ---------------------- Usuários ----------------------
        admins_data = [
            {"email": "admin1@solmaior.com", "full_name": "Helena Castro", "phone": "11990010001"},
            {"email": "admin2@solmaior.com", "full_name": "Rafael Martins", "phone": "11990010002"},
        ]
        secretaries_data = [
            {"email": "secretaria1@solmaior.com", "full_name": "Patrícia Souza", "phone": "11990020001"},
            {"email": "secretaria2@solmaior.com", "full_name": "Bruno Almeida", "phone": "11990020002"},
        ]
        teachers_data = [
            {
                "email": "prof.luiza@solmaior.com",
                "full_name": "Luiza Ferraz",
                "phone": "11990030001",
                "instrument": "Piano",
                "specialization": "Piano Clássico",
            },
            {
                "email": "prof.diego@solmaior.com",
                "full_name": "Diego Rodrigues",
                "phone": "11990030002",
                "instrument": "Violão",
                "specialization": "MPB e Jazz",
            },
            {
                "email": "prof.carolina@solmaior.com",
                "full_name": "Carolina Nogueira",
                "phone": "11990030003",
                "instrument": "Canto",
                "specialization": "Canto Popular",
            },
        ]
        students_data = [
            {
                "email": "aluno.arthur@solmaior.com",
                "full_name": "Arthur Silva",
                "phone": "11990040001",
                "instrument": "Piano",
                "level": "Intermediário",
            },
            {
                "email": "aluna.marina@solmaior.com",
                "full_name": "Marina Costa",
                "phone": "11990040002",
                "instrument": "Violão",
                "level": "Iniciante",
            },
            {
                "email": "aluna.isabela@solmaior.com",
                "full_name": "Isabela Prado",
                "phone": "11990040003",
                "instrument": "Canto",
                "level": "Avançado",
            },
        ]

        users_created = []

        for data in admins_data:
            user = get_or_create_user(role="admin", **data)
            users_created.append({"email": user.email, "role": user.role})

        for data in secretaries_data:
            user = get_or_create_user(role="secretary", **data)
            users_created.append({"email": user.email, "role": user.role})

        teachers = []
        for data in teachers_data:
            instrument = data.pop("instrument")
            specialization = data.pop("specialization")
            user = get_or_create_user(role="teacher", **data)
            teacher = ensure_teacher(user, instrument, specialization)
            teachers.append(teacher)
            users_created.append({"email": user.email, "role": user.role})

        students = []
        for data in students_data:
            instrument = data.pop("instrument")
            level = data.pop("level")
            extra = {
                "guardian_name": "Responsável Sol Maior",
                "city": "São Paulo",
                "state": "SP",
            }
            user = get_or_create_user(role="student", **data)
            student = ensure_student(user, instrument, level, **extra)
            students.append(student)
            users_created.append({"email": user.email, "role": user.role})

        db.session.commit()

        # ---------------------- Salas ----------------------
        rooms_seed = [
            ("Sala Beethoven", 4, "Piano de cauda, metronomo"),
            ("Sala Villa-Lobos", 3, "Violões, amplificador"),
            ("Sala Elis Regina", 2, "Microfones, retorno"),
            ("Sala Tom Jobim", 5, "Bateria, teclado"),
            ("Sala Choro", 2, "Bandolim, cavaquinho"),
        ]
        rooms = []
        for name, capacity, equipment in rooms_seed:
            room = Room.query.filter_by(name=name).first()
            if not room:
                room = Room(name=name, capacity=capacity, equipment=equipment)
                db.session.add(room)
            rooms.append(room)
        db.session.commit()

        # ---------------------- Recitais ----------------------
        recital_base_date = datetime.now().replace(hour=19, minute=0, second=0, microsecond=0)
        recitals = []
        for i in range(5):
            title = f"Recital de Primavera #{i + 1}"
            recital = Recital.query.filter_by(title=title).first()
            if not recital:
                recital = Recital(
                    title=title,
                    description="Apresentações coletivas dos alunos em destaque.",
                    event_date=recital_base_date + timedelta(days=14 * i),
                    location="Auditório Sol Maior",
                    status="confirmed",
                    created_by=users_data_id("admin1@solmaior.com"),
                )
                db.session.add(recital)
                db.session.flush()
            recitals.append(recital)

        db.session.commit()

        # Performances (1 por recital)
        for idx, recital in enumerate(recitals):
            performance = RecitalPerformance.query.filter_by(recital_id=recital.id, order_number=1).first()
            if performance:
                continue
            student = students[idx % len(students)]
            teacher = teachers[idx % len(teachers)]
            performance = RecitalPerformance(
                recital_id=recital.id,
                performance_type="solo",
                piece_title=f"Peça Demonstração {idx + 1}",
                composer="Sol Maior",
                duration_minutes=5 + idx,
                order_number=1,
            )
            db.session.add(performance)
            db.session.flush()

            db.session.add_all(
                [
                    RecitalParticipant(performance_id=performance.id, student_id=student.id, role="performer", confirmed=True),
                    RecitalParticipant(performance_id=performance.id, teacher_id=teacher.id, role="accompanist", confirmed=True),
                ]
            )
        db.session.commit()

        # ---------------------- Agenda ----------------------
        lessons_created = []
        start_date = date.today() + timedelta(days=1)
        for idx, student in enumerate(students):
            teacher = teachers[idx % len(teachers)]
            room = rooms[idx % len(rooms)]
            lesson_date = start_date + timedelta(days=idx)
            lesson = LessonSchedule.query.filter_by(
                teacher_id=teacher.id,
                student_id=student.id,
                lesson_date=lesson_date,
                start_time=datetime.strptime("18:00", "%H:%M").time(),
            ).first()
            if not lesson:
                lesson = LessonSchedule(
                    teacher_id=teacher.id,
                    student_id=student.id,
                    room_id=room.id,
                    lesson_date=lesson_date,
                    start_time=datetime.strptime("18:00", "%H:%M").time(),
                    end_time=datetime.strptime("19:00", "%H:%M").time(),
                    status="scheduled",
                    lesson_type="regular",
                    notes="Aula prática com preparação para recital.",
                )
                db.session.add(lesson)
            lessons_created.append(lesson)
        db.session.commit()

        # ---------------------- Financeiro ----------------------
        enrollments = []
        for idx, student in enumerate(students):
            plan_type = "mensal"
            enrollment = Enrollment.query.filter_by(student_id=student.id, status="active").first()
            if not enrollment:
                enrollment = Enrollment(
                    student_id=student.id,
                    plan_type=plan_type,
                    monthly_value=450.0,
                    start_date=date.today().replace(day=1),
                    status="active",
                )
                db.session.add(enrollment)
                db.session.flush()
            enrollments.append(enrollment)

            # Criar duas faturas: uma paga, outra pendente
            due_base = date.today().replace(day=10)
            payments = [
                {
                    "reference_month": due_base.replace(month=due_base.month - 1 if due_base.month > 1 else 12),
                    "due_date": due_base - timedelta(days=30),
                    "payment_date": due_base - timedelta(days=27),
                    "status": "paid",
                    "payment_method": "credit_card",
                },
                {
                    "reference_month": due_base,
                    "due_date": due_base,
                    "payment_date": None,
                    "status": "pending",
                    "payment_method": None,
                },
            ]
            for payment_data in payments:
                payment = Payment.query.filter_by(
                    enrollment_id=enrollment.id,
                    reference_month=payment_data["reference_month"],
                ).first()
                if payment:
                    continue
                payment = Payment(
                    enrollment_id=enrollment.id,
                    reference_month=payment_data["reference_month"],
                    due_date=payment_data["due_date"],
                    payment_date=payment_data["payment_date"],
                    amount=450.0,
                    discount=0.0,
                    late_fee=0.0,
                    total_amount=450.0,
                    payment_method=payment_data["payment_method"],
                    status=payment_data["status"],
                    receipt_number=f"REC{enrollment.id:03d}{payment_data['reference_month'].month:02d}{payment_data['reference_month'].year}",
                    notes="Mensalidade gerada automaticamente.",
                )
                db.session.add(payment)
        db.session.commit()

        # ---------------------- Documentos ----------------------
        documents_seed = [
            ("Contrato Arthur", "contract", students[0], None),
            ("Plano de Estudos Piano", "score", students[0], teachers[0]),
            ("Relatório Vocal", "audio", students[2], teachers[2]),
            ("Manual de Aulas", "other", None, None),
            ("Partitura Especial Violão", "score", students[1], teachers[1]),
        ]
        placeholder_path = "uploads/demo"
        for idx, (title, category, student_ref, teacher_ref) in enumerate(documents_seed, start=1):
            doc = Document.query.filter_by(title=title).first()
            if doc:
                continue
            doc = Document(
                title=title,
                description="Documento de exemplo para demonstração do sistema.",
                file_name=f"demo_{idx}.pdf",
                file_path=f"{placeholder_path}/demo_{idx}.pdf",
                file_type="application/pdf",
                file_size=1024 * idx,
                category=category,
                uploaded_by=users_data_id("admin1@solmaior.com"),
                related_student_id=student_ref.id if student_ref else None,
                related_teacher_id=teacher_ref.id if teacher_ref else None,
                is_public=category in {"other", "score"},
            )
            db.session.add(doc)
        db.session.commit()

        # ---------------------- Notícias ----------------------
        news_seed = [
            ("Festival de Inverno", "Confira a programação completa do festival anual."),
            ("Masterclass de Piano", "Inscrições abertas para masterclass exclusiva."),
            ("Campanha de Matrículas", "Promoção especial para novos alunos."),
            ("Recital Beneficente", "Evento beneficente com participação dos professores."),
            ("Workshop de Improvisação", "Aprenda técnicas com especialistas convidados."),
        ]
        for idx, (title, content) in enumerate(news_seed, start=1):
            post = NewsPost.query.filter_by(title=title).first()
            if post:
                continue
            post = NewsPost(
                title=title,
                content=content,
                author_id=users_data_id("admin2@solmaior.com"),
                post_type="news",
                is_published=True,
                published_at=datetime.utcnow() - timedelta(days=idx),
            )
            db.session.add(post)
        db.session.commit()

        # ---------------------- Automação ----------------------
        if not ScheduledNotification.query.filter_by(notification_type="lesson_reminder").first():
            first_lesson = lessons_created[0]
            notification = ScheduledNotification(
                notification_type="lesson_reminder",
                recipient_id=first_lesson.student.user.id,
                recipient_email=first_lesson.student.user.email,
                subject="Lembrete de aula",
                message="Olá! Lembrete da sua aula marcada para amanhã às 18h.",
                related_lesson_id=first_lesson.id,
                scheduled_for=datetime.utcnow() + timedelta(hours=12),
                status="pending",
            )
            db.session.add(notification)
            db.session.commit()

        # ---------------------- Export JSON ----------------------
        export = {
            "users": users_created,
            "rooms": [room.name for room in rooms],
            "recitals": [recital.title for recital in recitals],
            "lessons": [
                {
                    "student": lesson.student.user.full_name,
                    "teacher": lesson.teacher.user.full_name,
                    "date": lesson.lesson_date.isoformat(),
                    "room": lesson.room.name if lesson.room else None,
                }
                for lesson in lessons_created
            ],
            "payments": [
                {
                    "student": Enrollment.query.get(payment.enrollment_id).student.user.full_name,
                    "status": payment.status,
                    "due_date": payment.due_date.isoformat(),
                    "method": payment.payment_method,
                }
                for payment in Payment.query.order_by(Payment.due_date.desc()).limit(6)
            ],
            "documents": [doc.title for doc in Document.query.limit(5)],
            "news": [post.title for post in NewsPost.query.order_by(NewsPost.published_at.desc()).limit(5)],
        }

        export_path = DATA_DIR / "demo_data_snapshot.json"
        export_path.write_text(json.dumps(export, indent=2, ensure_ascii=False), encoding="utf-8")

        print("Dados de demonstração inseridos/atualizados com sucesso!")
        print(f"Arquivo de snapshot salvo em: {export_path}")
        print("Usuários criados (todos com senha padrão SolMaior@2025):")
        for item in users_created:
            print(f" - {item['role']}: {item['email']}")


def users_data_id(email: str) -> int:
    user = User.query.filter_by(email=email).first()
    if not user:
        raise RuntimeError(f"Usuário '{email}' não encontrado. Execute o seed na ordem correta.")
    return user.id


if __name__ == "__main__":
    main()
