from app.services.security.context import SecurityContext


class SecurityPolicy:

    @staticmethod
    def can_access_tenant(
        context: SecurityContext,
        tenant_id: str,
    ) -> bool:
        """
        Check whether the caller belongs to the requested tenant.
        """
        return context.tenant_id == tenant_id

    @staticmethod
    def can_ingest_document(
        context: SecurityContext,
        tenant_id: str,
    ) -> bool:
        """
        Check whether the caller is allowed to ingest
        a document belonging to the specified tenant.
        """
        return (
            SecurityPolicy.can_access_tenant(
                context,
                tenant_id,
            )
            and "document:write" in context.permissions
        )


    @staticmethod
    def can_retrieve_document(
        context: SecurityContext,
        tenant_id: str,
    ) -> bool:
        """
        Check whether the caller is allowed to retrieve
        documents belonging to the specified tenant.
        """
        return (
            SecurityPolicy.can_access_tenant(
                context,
                tenant_id,
            )
            and "document:read" in context.permissions
        )