import React, { useState } from 'react';

/**
 * 标签项接口
 */
interface TabItem {
  id: string;
  label: string;
  content: React.ReactNode;
}

/**
 * 标签容器组件属性
 */
interface TabContainerProps {
  tabs: TabItem[];
  defaultTab?: string;
}

/**
 * 标签容器组件
 * 提供标签页布局，支持多个标签页切换
 */
const TabContainer: React.FC<TabContainerProps> = ({ tabs, defaultTab }) => {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id || '');

  /**
   * 处理标签切换
   */
  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
  };

  return (
    <div className="tab-container">
      <div className="tab-header">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'tab-button--active' : ''}`}
            onClick={() => handleTabChange(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="tab-content">
        {tabs.find(tab => tab.id === activeTab)?.content}
      </div>
    </div>
  );
};

export default TabContainer;
