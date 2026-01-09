from backend.models.user import Role


class InstructorService:
    @staticmethod
    def view_report(user, report):
        if user.role != Role.INSTRUCTOR:
            raise PermissionError("Instructor access only")
        return report
