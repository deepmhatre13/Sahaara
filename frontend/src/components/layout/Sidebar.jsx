import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Heart,
  Activity,
  AlertTriangle,
  Users,
  Bot,
  FileText,
  Pill,
  Calendar,
  Bell,
  LogOut,
  X,
} from 'lucide-react';
import useAuth from '../../hooks/useAuth';

export const Sidebar = ({ isOpen, onClose }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
    onClose?.();
  };

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Health Snapshot', path: '/health', icon: Heart },
    { label: 'Activity Monitor', path: '/activity', icon: Activity },
    { label: 'Emergency SOS', path: '/sos', icon: AlertTriangle },
    { label: 'Caregiver Network', path: '/caregiver', icon: Users },
    { label: 'AI Health Assistant', path: '/chatbot', icon: Bot },
    { label: 'Medical Reports', path: '/reports', icon: FileText },
    { label: 'Medications', path: '/medications', icon: Pill },
    { label: 'Appointments', path: '/appointments', icon: Calendar },
    { label: 'Notifications', path: '/notifications', icon: Bell },
  ];

  const sidebarContent = (
    <div className="flex flex-col h-full bg-white border-r border-[#DDE3E8] w-64 p-4">
      {/* Brand Header */}
      <div className="flex items-center justify-between px-2 py-4 mb-2">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[#1E3A5F] rounded-xl flex items-center justify-center text-white font-black text-xl shadow-xs">
            S
          </div>
          <div>
            <h1 className="font-extrabold text-lg text-[#1E3A5F] leading-tight">Sahaara</h1>
            <p className="text-[10px] font-semibold text-[#8A97A5] tracking-wide uppercase">Intelligent Care</p>
          </div>
        </div>
        {onClose && (
          <button onClick={onClose} className="md:hidden p-1 text-[#8A97A5] hover:text-[#1C2733]">
            <X size={20} />
          </button>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 space-y-1 overflow-y-auto py-2 pr-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all ${
                  isActive
                    ? 'bg-[#1E3A5F] text-white shadow-xs'
                    : 'text-[#1C2733] hover:bg-[#F4F1EC] hover:text-[#1E3A5F]'
                }`
              }
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* User Profile & Logout Bottom Bar */}
      <div className="border-t border-[#DDE3E8] pt-4 mt-2">
        <div className="flex items-center justify-between p-2 rounded-xl bg-[#F4F1EC]/60">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-[#1E3A5F]/10 text-[#1E3A5F] font-bold flex items-center justify-center text-xs">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-bold text-[#1C2733] truncate">{user?.full_name || 'Care Seeker'}</p>
              <p className="text-[10px] text-[#8A97A5] truncate">{user?.email || ''}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            title="Sign Out"
            className="p-1.5 text-[#8A97A5] hover:text-[#C0392B] rounded-lg transition-colors cursor-pointer"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className="hidden md:block h-screen sticky top-0 shrink-0">{sidebarContent}</aside>

      {/* Mobile Drawer Overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          <div className="fixed inset-0 bg-black/40 backdrop-blur-xs" onClick={onClose} />
          <div className="relative z-10">{sidebarContent}</div>
        </div>
      )}
    </>
  );
};

export default Sidebar;
