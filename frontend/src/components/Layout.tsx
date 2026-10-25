import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';
import { TransactionModal } from './TransactionModal';

export const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [newTxnModalOpen, setNewTxnModalOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 md:pl-64">
        {/* Navbar */}
        <Navbar
          onOpenSidebar={() => setSidebarOpen(true)}
          onOpenNewTransaction={() => setNewTxnModalOpen(true)}
          onRefreshData={handleRefresh}
        />

        {/* Page Content with key for forced refresh upon seeding */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto" key={refreshKey}>
          <Outlet context={{ refreshTrigger: refreshKey, onRefresh: handleRefresh }} />
        </main>
      </div>

      {/* Global Transaction Modal */}
      <TransactionModal
        isOpen={newTxnModalOpen}
        onClose={() => setNewTxnModalOpen(false)}
        onSuccess={handleRefresh}
      />
    </div>
  );
};
