import React, { useState } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart,
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  Globe,
  Star,
  DollarSign,
  Users,
  BarChart3,
  MessageSquare,
  FileText,
  Search,
  Filter,
  Download,
  RefreshCw,
  ChevronRight,
  Activity,
  ShoppingCart,
  Target,
  Zap,
  Shield,
  Clock,
  MapPin,
  Award,
} from 'lucide-react';

interface CompetitorData {
  id: string;
  name: string;
  website: string;
  rating: number;
  marketShare: number;
  sentimentScore: number;
  financialHealth: number;
  priceIndex: number;
  seoScore: number;
  loadTime: number;
  reviewCount: number;
}

const CompetitorAnalysisDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedCompetitor, setSelectedCompetitor] = useState<string>('all');
  const [timeRange, setTimeRange] = useState('30d');
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Mock data for competitors
  const competitors: CompetitorData[] = [
    {
      id: '1',
      name: 'Вкусно и точка',
      website: 'vkusnoitochka.ru',
      rating: 4.2,
      marketShare: 18,
      sentimentScore: 72,
      financialHealth: 85,
      priceIndex: 95,
      seoScore: 88,
      loadTime: 2.3,
      reviewCount: 15420,
    },
    {
      id: '2',
      name: 'Теремок',
      website: 'teremok.ru',
      rating: 4.5,
      marketShare: 12,
      sentimentScore: 81,
      financialHealth: 78,
      priceIndex: 102,
      seoScore: 92,
      loadTime: 1.8,
      reviewCount: 12350,
    },
    {
      id: '3',
      name: 'Шоколадница',
      website: 'shoko.ru',
      rating: 4.3,
      marketShare: 15,
      sentimentScore: 76,
      financialHealth: 82,
      priceIndex: 110,
      seoScore: 85,
      loadTime: 2.1,
      reviewCount: 18900,
    },
    {
      id: '4',
      name: 'Кофемания',
      website: 'coffeemania.ru',
      rating: 4.6,
      marketShare: 8,
      sentimentScore: 88,
      financialHealth: 90,
      priceIndex: 125,
      seoScore: 90,
      loadTime: 1.5,
      reviewCount: 8750,
    },
  ];

  // Performance metrics over time
  const performanceData = [
    {
      month: 'Янв',
      competitor1: 85,
      competitor2: 78,
      competitor3: 82,
      competitor4: 90,
    },
    {
      month: 'Фев',
      competitor1: 87,
      competitor2: 80,
      competitor3: 84,
      competitor4: 88,
    },
    {
      month: 'Мар',
      competitor1: 86,
      competitor2: 82,
      competitor3: 85,
      competitor4: 91,
    },
    {
      month: 'Апр',
      competitor1: 88,
      competitor2: 85,
      competitor3: 83,
      competitor4: 92,
    },
    {
      month: 'Май',
      competitor1: 90,
      competitor2: 87,
      competitor3: 86,
      competitor4: 93,
    },
    {
      month: 'Июн',
      competitor1: 92,
      competitor2: 88,
      competitor3: 88,
      competitor4: 94,
    },
  ];

  // Sentiment analysis data
  const sentimentData = [
    { name: 'Положительные', value: 65, color: '#10b981' },
    { name: 'Нейтральные', value: 25, color: '#6b7280' },
    { name: 'Отрицательные', value: 10, color: '#ef4444' },
  ];

  // Review topics
  const reviewTopics = [
    { topic: 'Качество еды', positive: 78, negative: 22 },
    { topic: 'Обслуживание', positive: 82, negative: 18 },
    { topic: 'Цены', positive: 45, negative: 55 },
    { topic: 'Атмосфера', positive: 71, negative: 29 },
    { topic: 'Чистота', positive: 88, negative: 12 },
    { topic: 'Скорость', positive: 66, negative: 34 },
  ];

  // Financial metrics
  const financialData = [
    { metric: 'Выручка', value: 85, benchmark: 75 },
    { metric: 'Рентабельность', value: 72, benchmark: 68 },
    { metric: 'Ликвидность', value: 90, benchmark: 80 },
    { metric: 'Долговая нагрузка', value: 35, benchmark: 45 },
    { metric: 'Рост', value: 78, benchmark: 70 },
  ];

  // Marketing channels
  const marketingChannels = [
    { channel: 'Instagram', reach: 45000, engagement: 4.2, cost: 85000 },
    { channel: 'VK', reach: 38000, engagement: 3.8, cost: 62000 },
    { channel: 'Яндекс.Директ', reach: 52000, engagement: 2.1, cost: 120000 },
    { channel: 'Google Ads', reach: 28000, engagement: 2.5, cost: 95000 },
    { channel: 'Telegram', reach: 15000, engagement: 5.1, cost: 35000 },
  ];

  // Price comparison
  const priceComparison = [
    { category: 'Бизнес-ланч', comp1: 350, comp2: 420, comp3: 480, comp4: 550 },
    { category: 'Кофе', comp1: 180, comp2: 200, comp3: 220, comp4: 280 },
    { category: 'Десерты', comp1: 250, comp2: 280, comp3: 320, comp4: 380 },
    { category: 'Салаты', comp1: 320, comp2: 380, comp3: 420, comp4: 480 },
    {
      category: 'Основные блюда',
      comp1: 450,
      comp2: 520,
      comp3: 580,
      comp4: 650,
    },
  ];

  // SEO metrics
  const seoMetrics = [
    { metric: 'Скорость загрузки', current: 2.1, optimal: 1.5, unit: 'сек' },
    { metric: 'Mobile-friendly', current: 92, optimal: 100, unit: '%' },
    { metric: 'Индексация', current: 85, optimal: 95, unit: '%' },
    { metric: 'Обратные ссылки', current: 1250, optimal: 2000, unit: 'шт' },
    {
      metric: 'Органический трафик',
      current: 45000,
      optimal: 60000,
      unit: 'визитов',
    },
  ];

  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setLastUpdate(new Date());
    }, 1500);
  };

  // Вспомогательная функция для получения имени конкурента по ID
  const getCompetitorName = (id: string) => {
    const competitor = competitors.find(comp => comp.id === id);
    return competitor ? competitor.name : 'Все конкуренты';
  };

  // Вспомогательная функция для фильтрации данных
  const getFilteredData = () => {
    if (selectedCompetitor === 'all') {
      return {
        competitors: competitors,
        performanceData: performanceData,
        showAll: true
      };
    }
    
    const filteredCompetitor = competitors.find(comp => comp.id === selectedCompetitor);
    return {
      competitors: filteredCompetitor ? [filteredCompetitor] : [],
      performanceData: performanceData.map(item => {
        const competitorKey = `competitor${selectedCompetitor}`;
        return {
          month: item.month,
          [competitorKey]: item[competitorKey]
        };
      }),
      showAll: false
    };
  };

  // Функция для получения отфильтрованных данных отзывов
  const getFilteredReviewData = () => {
    if (selectedCompetitor === 'all') {
      return reviewTopics;
    }
    
    // Симулируем разные данные для разных конкурентов
    const competitorReviewData: Record<string, any[]> = {
      '1': [
        { topic: 'Качество еды', positive: 82, negative: 18 },
        { topic: 'Обслуживание', positive: 75, negative: 25 },
        { topic: 'Цены', positive: 60, negative: 40 },
        { topic: 'Атмосфера', positive: 68, negative: 32 },
        { topic: 'Чистота', positive: 85, negative: 15 },
        { topic: 'Скорость', positive: 70, negative: 30 },
      ],
      '2': [
        { topic: 'Качество еды', positive: 88, negative: 12 },
        { topic: 'Обслуживание', positive: 90, negative: 10 },
        { topic: 'Цены', positive: 50, negative: 50 },
        { topic: 'Атмосфера', positive: 80, negative: 20 },
        { topic: 'Чистота', positive: 92, negative: 8 },
        { topic: 'Скорость', positive: 75, negative: 25 },
      ],
      '3': [
        { topic: 'Качество еды', positive: 85, negative: 15 },
        { topic: 'Обслуживание', positive: 78, negative: 22 },
        { topic: 'Цены', positive: 40, negative: 60 },
        { topic: 'Атмосфера', positive: 85, negative: 15 },
        { topic: 'Чистота', positive: 88, negative: 12 },
        { topic: 'Скорость', positive: 65, negative: 35 },
      ],
      '4': [
        { topic: 'Качество еды', positive: 92, negative: 8 },
        { topic: 'Обслуживание', positive: 88, negative: 12 },
        { topic: 'Цены', positive: 35, negative: 65 },
        { topic: 'Атмосфера', positive: 90, negative: 10 },
        { topic: 'Чистота', positive: 95, negative: 5 },
        { topic: 'Скорость', positive: 80, negative: 20 },
      ]
    };
    
    return competitorReviewData[selectedCompetitor] || reviewTopics;
  };

  // Функция для получения отфильтрованных финансовых данных
  const getFilteredFinancialData = () => {
    if (selectedCompetitor === 'all') {
      return financialData;
    }
    
    const competitorFinancialData: Record<string, any[]> = {
      '1': [
        { metric: 'Выручка', value: 85, benchmark: 75 },
        { metric: 'Рентабельность', value: 72, benchmark: 68 },
        { metric: 'Ликвидность', value: 90, benchmark: 80 },
        { metric: 'Долговая нагрузка', value: 35, benchmark: 45 },
        { metric: 'Рост', value: 78, benchmark: 70 },
      ],
      '2': [
        { metric: 'Выручка', value: 78, benchmark: 75 },
        { metric: 'Рентабельность', value: 68, benchmark: 68 },
        { metric: 'Ликвидность', value: 85, benchmark: 80 },
        { metric: 'Долговая нагрузка', value: 42, benchmark: 45 },
        { metric: 'Рост', value: 72, benchmark: 70 },
      ],
      '3': [
        { metric: 'Выручка', value: 82, benchmark: 75 },
        { metric: 'Рентабельность', value: 75, benchmark: 68 },
        { metric: 'Ликвидность', value: 88, benchmark: 80 },
        { metric: 'Долговая нагрузка', value: 38, benchmark: 45 },
        { metric: 'Рост', value: 80, benchmark: 70 },
      ],
      '4': [
        { metric: 'Выручка', value: 90, benchmark: 75 },
        { metric: 'Рентабельность', value: 82, benchmark: 68 },
        { metric: 'Ликвидность', value: 92, benchmark: 80 },
        { metric: 'Долговая нагрузка', value: 28, benchmark: 45 },
        { metric: 'Рост', value: 85, benchmark: 70 },
      ]
    };
    
    return competitorFinancialData[selectedCompetitor] || financialData;
  };

  // Функция для получения отфильтрованных данных маркетинга
  const getFilteredMarketingData = () => {
    if (selectedCompetitor === 'all') {
      return marketingChannels;
    }
    
    const competitorMarketingData: Record<string, any[]> = {
      '1': [
        { channel: 'Instagram', reach: 45000, engagement: 4.2, cost: 85000 },
        { channel: 'VK', reach: 38000, engagement: 3.8, cost: 62000 },
        { channel: 'Яндекс.Директ', reach: 52000, engagement: 2.1, cost: 120000 },
        { channel: 'Google Ads', reach: 28000, engagement: 2.5, cost: 95000 },
        { channel: 'Telegram', reach: 15000, engagement: 5.1, cost: 35000 },
      ],
      '2': [
        { channel: 'Instagram', reach: 32000, engagement: 3.8, cost: 65000 },
        { channel: 'VK', reach: 28000, engagement: 4.1, cost: 45000 },
        { channel: 'Яндекс.Директ', reach: 38000, engagement: 2.3, cost: 85000 },
        { channel: 'Google Ads', reach: 22000, engagement: 2.8, cost: 72000 },
        { channel: 'Telegram', reach: 12000, engagement: 4.8, cost: 28000 },
      ],
      '3': [
        { channel: 'Instagram', reach: 52000, engagement: 4.5, cost: 98000 },
        { channel: 'VK', reach: 42000, engagement: 3.5, cost: 75000 },
        { channel: 'Яндекс.Директ', reach: 58000, engagement: 1.9, cost: 135000 },
        { channel: 'Google Ads', reach: 32000, engagement: 2.2, cost: 110000 },
        { channel: 'Telegram', reach: 18000, engagement: 5.3, cost: 42000 },
      ],
      '4': [
        { channel: 'Instagram', reach: 38000, engagement: 4.8, cost: 72000 },
        { channel: 'VK', reach: 25000, engagement: 4.2, cost: 38000 },
        { channel: 'Яндекс.Директ', reach: 32000, engagement: 2.4, cost: 68000 },
        { channel: 'Google Ads', reach: 18000, engagement: 3.1, cost: 52000 },
        { channel: 'Telegram', reach: 8000, engagement: 6.2, cost: 18000 },
      ]
    };
    
    return competitorMarketingData[selectedCompetitor] || marketingChannels;
  };

  // Функция для получения отфильтрованных цен
  const getFilteredPriceData = () => {
    if (selectedCompetitor === 'all') {
      return priceComparison;
    }
    
    // Для конкретного конкурента показываем только его цены
    const competitorIndex = parseInt(selectedCompetitor);
    return priceComparison.map(item => ({
      category: item.category,
      price: item[`comp${competitorIndex}` as keyof typeof item]
    }));
  };

  const MetricCard = ({ title, value, change, icon: Icon, color }: any) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-600">{title}</span>
        <Icon className={`w-5 h-5 ${color}`} />
      </div>
      <div className="flex items-baseline justify-between">
        <span className="text-2xl font-bold text-gray-900">{value}</span>
        {change && (
          <div
            className={`flex items-center text-sm ${
              change > 0 ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {change > 0 ? (
              <TrendingUp className="w-4 h-4 mr-1" />
            ) : (
              <TrendingDown className="w-4 h-4 mr-1" />
            )}
            {Math.abs(change)}%
          </div>
        )}
      </div>
    </div>
  );

  const renderOverview = () => {
    const { competitors: filteredCompetitors, performanceData: filteredPerformanceData } = getFilteredData();
  
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Средний рейтинг"
            value={selectedCompetitor === 'all' ? "4.4" : filteredCompetitors[0]?.rating.toFixed(1)}
            change={5}
            icon={Star}
            color="text-yellow-500"
          />
          <MetricCard
            title="Доля рынка"
            value={selectedCompetitor === 'all' ? "53%" : `${filteredCompetitors[0]?.marketShare}%`}
            change={-2}
            icon={BarChart3}
            color="text-blue-500"
          />
          <MetricCard
            title="Sentiment Score"
            value={selectedCompetitor === 'all' ? "79%" : `${filteredCompetitors[0]?.sentimentScore}%`}
            change={8}
            icon={MessageSquare}
            color="text-green-500"
          />
          <MetricCard
            title="SEO Score"
            value={selectedCompetitor === 'all' ? "88" : filteredCompetitors[0]?.seoScore.toString()}
            change={12}
            icon={Globe}
            color="text-purple-500"
          />
        </div>
  
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Динамика производительности</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={filteredPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                {selectedCompetitor === 'all' || selectedCompetitor === '1' ? (
                  <Line type="monotone" dataKey="competitor1" stroke="#3b82f6" name="Вкусно и точка" strokeWidth={2} />
                ) : null}
                {selectedCompetitor === 'all' || selectedCompetitor === '2' ? (
                  <Line type="monotone" dataKey="competitor2" stroke="#10b981" name="Теремок" strokeWidth={2} />
                ) : null}
                {selectedCompetitor === 'all' || selectedCompetitor === '3' ? (
                  <Line type="monotone" dataKey="competitor3" stroke="#f59e0b" name="Шоколадница" strokeWidth={2} />
                ) : null}
                {selectedCompetitor === 'all' || selectedCompetitor === '4' ? (
                  <Line type="monotone" dataKey="competitor4" stroke="#8b5cf6" name="Кофемания" strokeWidth={2} />
                ) : null}
              </LineChart>
            </ResponsiveContainer>
          </div>
  
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">
              {selectedCompetitor === 'all' ? 'Рейтинг конкурентов' : 'Детали конкурента'}
            </h3>
            <div className="space-y-4">
              {filteredCompetitors.map((comp, index) => (
                <div key={comp.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <span className="text-lg font-bold text-gray-400">
                      {selectedCompetitor === 'all' ? `#${index + 1}` : '⭐'}
                    </span>
                    <div>
                      <p className="font-medium text-gray-900">{comp.name}</p>
                      <p className="text-sm text-gray-500">{comp.website}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center">
                      <Star className="w-4 h-4 text-yellow-500 mr-1" />
                      <span className="font-medium">{comp.rating}</span>
                    </div>
                    <div className="text-sm text-gray-600">
                      {comp.marketShare}% рынка
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderTechnicalAnalysis = () => {
    const { competitors: filteredCompetitors } = getFilteredData();
    
    return (
      <div className="space-y-6">
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Технический анализ {selectedCompetitor !== 'all' ? `- ${getCompetitorName(selectedCompetitor)}` : ''}
          </h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Исправленный блок SEO метрик */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">SEO метрики</h3>
            <div className="space-y-4">
              {seoMetrics.map((metric) => (
                <div key={metric.metric} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">{metric.metric}</span>
                    <span className="font-medium">
                      {metric.current} {metric.unit}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        metric.metric === 'Скорость загрузки' 
                          ? (metric.current <= 1.5 ? 'bg-green-500' : metric.current <= 3 ? 'bg-yellow-500' : 'bg-red-500')
                          : 'bg-blue-600'
                      }`}
                      style={{
                        width: metric.metric === 'Скорость загрузки' 
                          ? `${Math.min((1 / metric.current) * 100, 100)}%`
                          : `${(metric.current / metric.optimal) * 100}%`,
                      }}
                    />
                  </div>
                  {metric.metric === 'Скорость загрузки' && (
                    <div className="text-xs text-gray-500">
                      Оптимально: {metric.optimal} {metric.unit}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Исправленный график скорости загрузки */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">
              Скорость загрузки сайтов
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={filteredCompetitors.map((c) => ({
                  name: c.name,
                  loadTime: c.loadTime,
                  fill: c.loadTime < 2 ? '#10b981' : c.loadTime < 3 ? '#f59e0b' : '#ef4444'
                }))}
                margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  angle={-45} 
                  textAnchor="end" 
                  height={80}
                  interval={0}
                  tick={{ fontSize: 12 }}
                />
                <YAxis />
                <Tooltip 
                  formatter={(value) => [`${value} сек`, 'Скорость загрузки']}
                  labelFormatter={(label) => `Сайт: ${label}`}
                />
                <Bar 
                  dataKey="loadTime" 
                  name="Скорость загрузки"
                  radius={[4, 4, 0, 0]}
                >
                  {filteredCompetitors.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.loadTime < 2 ? '#10b981' : entry.loadTime < 3 ? '#f59e0b' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Остальной код остается без изменений */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold mb-4">Технический аудит</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { label: 'SSL сертификат', status: 'active', icon: Shield },
              { label: 'Mobile-friendly', status: 'active', icon: Zap },
              { label: 'Скорость загрузки', status: 'warning', icon: Clock },
              { label: 'Структура URL', status: 'active', icon: Globe },
              { label: 'XML Sitemap', status: 'active', icon: FileText },
              { label: 'Robots.txt', status: 'error', icon: AlertCircle },
            ].map((item) => (
              <div
                key={item.label}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-2">
                  <item.icon className="w-4 h-4 text-gray-600" />
                  <span className="text-sm font-medium">{item.label}</span>
                </div>
                <div
                  className={`w-2 h-2 rounded-full ${
                    item.status === 'active'
                      ? 'bg-green-500'
                      : item.status === 'warning'
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderReviewAnalysis = () => {
    const filteredReviewData = getFilteredReviewData();
    
    return (
      <div className="space-y-6">
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Анализ отзывов {selectedCompetitor !== 'all' ? `- ${getCompetitorName(selectedCompetitor)}` : ''}
          </h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* График тональности отзывов остается без изменений */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Тональность отзывов</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {sentimentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {sentimentData.map((item) => (
                <div
                  key={item.name}
                  className="flex items-center justify-between"
                >
                  <div className="flex items-center">
                    <div
                      className={`w-3 h-3 rounded-full mr-2`}
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="text-sm">{item.name}</span>
                  </div>
                  <span className="text-sm font-medium">{item.value}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Исправленный график анализа по темам */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Анализ по темам</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={filteredReviewData}
                layout="vertical"
                margin={{ top: 20, right: 30, left: 100, bottom: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
                <XAxis 
                  type="number" 
                  domain={[0, 100]}
                  tickFormatter={(value) => `${value}%`}
                />
                <YAxis 
                  dataKey="topic" 
                  type="category" 
                  width={90}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip 
                  formatter={(value) => [`${value}%`, '']}
                  labelFormatter={(label) => `Тема: ${label}`}
                />
                <Legend />
                <Bar 
                  dataKey="positive" 
                  name="Положительные отзывы" 
                  fill="#10b981"
                  radius={[0, 4, 4, 0]}
                  stackId="a"
                />
                <Bar 
                  dataKey="negative" 
                  name="Отрицательные отзывы" 
                  fill="#ef4444"
                  radius={[0, 4, 4, 0]}
                  stackId="a"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Остальной код остается без изменений */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold mb-4">Последние отзывы</h3>
          <div className="space-y-4">
            {[
              {
                author: 'Мария К.',
                rating: selectedCompetitor === 'all' ? 5 : competitors.find(c => c.id === selectedCompetitor)?.rating || 5,
                text: selectedCompetitor === 'all' ? 'Отличное обслуживание и вкусная еда!' : `Отличное обслуживание в ${getCompetitorName(selectedCompetitor)}!`,
                date: '2 часа назад',
                sentiment: 'positive',
              },
              {
                author: 'Иван П.',
                rating: 3,
                text: 'Долго ждали заказ, но еда была хорошая',
                date: '5 часов назад',
                sentiment: 'neutral',
              },
              {
                author: 'Елена С.',
                rating: 4,
                text: 'Приятная атмосфера, рекомендую',
                date: '1 день назад',
                sentiment: 'positive',
              },
              {
                author: 'Дмитрий Л.',
                rating: 2,
                text: 'Цены завышены для такого качества',
                date: '2 дня назад',
                sentiment: 'negative',
              },
            ].map((review, index) => (
              <div key={index} className="border-l-4 border-gray-200 pl-4 py-2">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">{review.author}</span>
                    <div className="flex">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-4 h-4 ${
                            i < review.rating
                              ? 'text-yellow-500 fill-current'
                              : 'text-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                  </div>
                  <span className="text-sm text-gray-500">{review.date}</span>
                </div>
                <p className="text-gray-700">{review.text}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderFinancialAnalysis = () => {
    const filteredFinancialData = getFilteredFinancialData();
    const { competitors: filteredCompetitors } = getFilteredData();
    
    return (
      <div className="space-y-6">
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Финансовый анализ {selectedCompetitor !== 'all' ? `- ${getCompetitorName(selectedCompetitor)}` : ''}
          </h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Финансовые показатели</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={filteredFinancialData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name="Текущие"
                  dataKey="value"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.6}
                />
                <Radar
                  name="Benchmark"
                  dataKey="benchmark"
                  stroke="#10b981"
                  fill="#10b981"
                  fillOpacity={0.3}
                />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Прогноз выручки</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={getFilteredData().performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                {selectedCompetitor === 'all' || selectedCompetitor === '1' ? (
                  <Area type="monotone" dataKey="competitor1" stackId="1" stroke="#3b82f6" fill="#3b82f6" name="Вкусно и точка" />
                ) : null}
                {selectedCompetitor === 'all' || selectedCompetitor === '2' ? (
                  <Area type="monotone" dataKey="competitor2" stackId="1" stroke="#10b981" fill="#10b981" name="Теремок" />
                ) : null}
                {selectedCompetitor === 'all' || selectedCompetitor === '3' ? (
                  <Area type="monotone" dataKey="competitor3" stackId="1" stroke="#f59e0b" fill="#f59e0b" name="Шоколадница" />
                ) : null}
                {selectedCompetitor === 'all' || selectedCompetitor === '4' ? (
                  <Area type="monotone" dataKey="competitor4" stackId="1" stroke="#8b5cf6" fill="#8b5cf6" name="Кофемания" />
                ) : null}
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold mb-4">Риск-анализ</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[
              {
                label: 'Риск банкротства',
                value: filteredCompetitors[0]?.financialHealth > 80 ? 'Низкий' : filteredCompetitors[0]?.financialHealth > 60 ? 'Средний' : 'Высокий',
                color: filteredCompetitors[0]?.financialHealth > 80 ? 'text-green-600' : filteredCompetitors[0]?.financialHealth > 60 ? 'text-yellow-600' : 'text-red-600',
                bgColor: filteredCompetitors[0]?.financialHealth > 80 ? 'bg-green-100' : filteredCompetitors[0]?.financialHealth > 60 ? 'bg-yellow-100' : 'bg-red-100',
              },
              {
                label: 'Кредитная нагрузка',
                value: 'Средняя',
                color: 'text-yellow-600',
                bgColor: 'bg-yellow-100',
              },
              {
                label: 'Ликвидность',
                value: filteredCompetitors[0]?.financialHealth > 85 ? 'Высокая' : 'Средняя',
                color: filteredCompetitors[0]?.financialHealth > 85 ? 'text-green-600' : 'text-yellow-600',
                bgColor: filteredCompetitors[0]?.financialHealth > 85 ? 'bg-green-100' : 'bg-yellow-100',
              },
              {
                label: 'Рентабельность',
                value: 'Средняя',
                color: 'text-yellow-600',
                bgColor: 'bg-yellow-100',
              },
            ].map((item) => (
              <div
                key={item.label}
                className="text-center p-4 bg-gray-50 rounded-lg"
              >
                <p className="text-sm text-gray-600 mb-2">{item.label}</p>
                <span
                  className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${item.color} ${item.bgColor}`}
                >
                  {item.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderMarketingAnalysis = () => {
    const filteredMarketingData = getFilteredMarketingData();
    
    return (
      <div className="space-y-6">
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Маркетинговый анализ {selectedCompetitor !== 'all' ? `- ${getCompetitorName(selectedCompetitor)}` : ''}
          </h2>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold mb-4">Маркетинговые каналы</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Канал
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Охват
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Engagement
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Стоимость
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ROI
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredMarketingData.map((channel) => (
                  <tr key={channel.channel}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {channel.channel}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {channel.reach.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {channel.engagement}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      ₽{channel.cost.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {(
                          ((channel.reach * channel.engagement) /
                            100 /
                            channel.cost) *
                          1000
                        ).toFixed(1)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Целевая аудитория</h3>
            <div className="space-y-4">
              {[
                { age: '18-24 года', percent: 15 },
                { age: '25-34 года', percent: 35 },
                { age: '35-44 года', percent: 30 },
                { age: '45+ лет', percent: 20 },
              ].map((item) => (
                <div key={item.age}>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium">{item.age}</span>
                    <span className="text-sm text-gray-600">{item.percent}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${item.percent}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Интересы аудитории</h3>
            <div className="flex flex-wrap gap-2">
              {[
                'Еда и рестораны',
                'Путешествия',
                'Здоровый образ жизни',
                'Семья',
                'Технологии',
                'Мода',
                'Спорт',
                'Музыка',
                'Кино',
              ].map((interest) => (
                <span
                  key={interest}
                  className="inline-block px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                >
                  {interest}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderPricingAnalysis = () => {
    const filteredPriceData = getFilteredPriceData();
    
    return (
      <div className="space-y-6">
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Ценовой анализ {selectedCompetitor !== 'all' ? `- ${getCompetitorName(selectedCompetitor)}` : ''}
          </h2>
        </div>

        {selectedCompetitor === 'all' ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">
              Сравнение цен по категориям
            </h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={priceComparison}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="comp1" fill="#3b82f6" name="Вкусно и точка" />
                <Bar dataKey="comp2" fill="#10b981" name="Теремок" />
                <Bar dataKey="comp3" fill="#f59e0b" name="Шоколадница" />
                <Bar dataKey="comp4" fill="#8b5cf6" name="Кофемания" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">
              Цены {getCompetitorName(selectedCompetitor)} по категориям
            </h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={filteredPriceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="price" fill="#3b82f6" name="Цена" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Ценовая эластичность</h3>
            <div className="space-y-4">
              {[
                { product: 'Бизнес-ланч', elasticity: -0.8, optimal: 380 },
                { product: 'Кофе', elasticity: -1.2, optimal: 210 },
                { product: 'Десерты', elasticity: -0.6, optimal: 290 },
                { product: 'Основные блюда', elasticity: -0.9, optimal: 520 },
              ].map((item) => (
                <div
                  key={item.product}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium">{item.product}</p>
                    <p className="text-sm text-gray-600">
                      Эластичность: {item.elasticity}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Оптимальная цена</p>
                    <p className="font-semibold text-lg">₽{item.optimal}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">
              Акции и скидки {selectedCompetitor !== 'all' ? getCompetitorName(selectedCompetitor) : 'конкурентов'}
            </h3>
            <div className="space-y-3">
              {[
                {
                  competitor: 'Вкусно и точка',
                  promo: 'Скидка 20% на второй кофе',
                  frequency: 'Ежедневно',
                },
                {
                  competitor: 'Теремок',
                  promo: 'Бизнес-ланч -15%',
                  frequency: 'Пн-Пт 12:00-16:00',
                },
                {
                  competitor: 'Шоколадница',
                  promo: 'Третий десерт бесплатно',
                  frequency: 'По выходным',
                },
                {
                  competitor: 'Кофемания',
                  promo: 'Карта лояльности 10%',
                  frequency: 'Постоянно',
                },
              ]
              .filter(item => selectedCompetitor === 'all' || item.competitor === getCompetitorName(selectedCompetitor))
              .map((item) => (
                <div
                  key={item.competitor}
                  className="border-l-4 border-blue-500 pl-4 py-2"
                >
                  <p className="font-medium">{item.competitor}</p>
                  <p className="text-sm text-gray-700">{item.promo}</p>
                  <p className="text-xs text-gray-500">{item.frequency}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Target className="w-8 h-8 text-blue-600" />
                <h1 className="text-2xl font-bold text-gray-900">
                  CompetitorAI
                </h1>
              </div>
              <span className="text-sm text-gray-500">
                Анализ конкурентов HoReCa
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <select
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
              >
                <option value="7d">7 дней</option>
                <option value="30d">30 дней</option>
                <option value="90d">90 дней</option>
                <option value="1y">1 год</option>
              </select>
              <button
                onClick={handleRefresh}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <RefreshCw
                  className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`}
                />
              </button>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2">
                <Download className="w-4 h-4" />
                <span>Экспорт</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { id: 'overview', label: 'Обзор', icon: BarChart3 },
              { id: 'technical', label: 'Технический анализ', icon: Globe },
              { id: 'reviews', label: 'Анализ отзывов', icon: MessageSquare },
              { id: 'financial', label: 'Финансы', icon: DollarSign },
              { id: 'marketing', label: 'Маркетинг', icon: Target },
              { id: 'pricing', label: 'Цены', icon: ShoppingCart },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2
                  ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Competitor Filter */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <select
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={selectedCompetitor}
              onChange={(e) => setSelectedCompetitor(e.target.value)}
            >
              <option value="all">Все конкуренты</option>
              {competitors.map((comp) => (
                <option key={comp.id} value={comp.id}>
                  {comp.name}
                </option>
              ))}
            </select>
            <button className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 flex items-center space-x-2">
              <Filter className="w-4 h-4" />
              <span>Фильтры</span>
            </button>
          </div>
          <div className="text-sm text-gray-500">
            {selectedCompetitor !== 'all' && (
              <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full mr-4">
                Просмотр: {getCompetitorName(selectedCompetitor)}
              </span>
            )}
            Последнее обновление: {lastUpdate.toLocaleTimeString('ru-RU')}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'technical' && renderTechnicalAnalysis()}
        {activeTab === 'reviews' && renderReviewAnalysis()}
        {activeTab === 'financial' && renderFinancialAnalysis()}
        {activeTab === 'marketing' && renderMarketingAnalysis()}
        {activeTab === 'pricing' && renderPricingAnalysis()}
      </main>

      {/* AI Insights Panel */}
      <div className="fixed bottom-6 right-6">
        <button className="bg-blue-600 text-white rounded-full p-4 shadow-lg hover:bg-blue-700 transition-colors flex items-center space-x-2">
          <Zap className="w-5 h-5" />
          <span className="pr-2">AI Insights</span>
        </button>
      </div>
    </div>
  );
};

export default CompetitorAnalysisDashboard;