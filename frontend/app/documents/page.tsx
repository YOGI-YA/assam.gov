'use client';

import { AppLayout } from '@/components/layout/AppLayout';
import { DocumentList } from '@/components/documents/DocumentList';

export default function DocumentsPage() {
  return (
    <AppLayout currentModule="Documents">
      <DocumentList />
    </AppLayout>
  );
}
