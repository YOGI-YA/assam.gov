'use client';

import { AppLayout } from '@/components/layout/AppLayout';
import { AuditLogTable } from '@/components/audit/AuditLogTable';

export default function AuditPage() {
  return (
    <AppLayout currentModule="Audit Logs">
      <AuditLogTable />
    </AppLayout>
  );
}
