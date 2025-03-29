import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '../components/ui/card';
import { statsAPI } from '../utils/api';
import { formatNumber } from '../lib/utils';
import { 
  Users, 
  Key, 
  FileText, 
  Activity, 
  TrendingUp
} from 'lucide-react';

const StatCard = ({ title, value, description, icon, loading, trend }) => {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          {title}
        </CardTitle>
        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {loading ? (
            <div className="h-2 w-24 bg-muted animate-pulse rounded-md" />
          ) : (
            value
          )}
        </div>
        <p className="text-xs text-muted-foreground mt-1 flex items-center">
          {description}
          {trend && (
            <span className={`ml-1 flex items-center ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {trend > 0 ? (
                <TrendingUp className="h-3 w-3 mr-1" />
              ) : (
                <TrendingUp className="h-3 w-3 mr-1 transform rotate-180" />
              )}
              {Math.abs(trend)}%
            </span>
          )}
        </p>
      </CardContent>
    </Card>
  );
};

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await statsAPI.getDashboardStats();
        setStats(response.data);
        setError(null);
      } catch (err) {
        setError('Impossible de charger les statistiques du tableau de bord');
        console.error('Error fetching dashboard stats:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  // Mock data for development (remove in production)
  const mockStats = {
    totalUsers: 843,
    activeUsers: 721,
    totalLicenses: 947,
    activeLicenses: 892,
    totalDocuments: 12864,
    usersTrend: 8.5,
    licensesTrend: 3.2,
    documentsTrend: 12.7
  };

  // Use mock data if no stats are available
  const displayStats = stats || mockStats;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Tableau de bord</h2>
        <p className="text-muted-foreground">
          Aperçu des statistiques de VynalDocs
        </p>
      </div>

      {error && (
        <div className="bg-destructive/15 text-destructive text-sm p-4 rounded-md">
          {error}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Utilisateurs"
          value={formatNumber(displayStats.totalUsers)}
          description="Utilisateurs totaux"
          icon={<Users className="h-4 w-4" />}
          loading={loading}
          trend={displayStats.usersTrend}
        />
        <StatCard
          title="Utilisateurs actifs"
          value={formatNumber(displayStats.activeUsers)}
          description={`${Math.round(displayStats.activeUsers / displayStats.totalUsers * 100)}% du total`}
          icon={<Activity className="h-4 w-4" />}
          loading={loading}
        />
        <StatCard
          title="Licences"
          value={formatNumber(displayStats.totalLicenses)}
          description="Licences totales"
          icon={<Key className="h-4 w-4" />}
          loading={loading}
          trend={displayStats.licensesTrend}
        />
        <StatCard
          title="Documents"
          value={formatNumber(displayStats.totalDocuments)}
          description="Documents générés"
          icon={<FileText className="h-4 w-4" />}
          loading={loading}
          trend={displayStats.documentsTrend}
        />
      </div>

      {/* Additional charts or metrics can be added here */}
    </div>
  );
};

export default Dashboard; 