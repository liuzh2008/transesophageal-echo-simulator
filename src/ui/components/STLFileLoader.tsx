import React, { useState, useCallback } from 'react';
import FileSelector from './FileSelector';
import LoadingIndicator from './LoadingIndicator';
import ErrorDisplay from './ErrorDisplay';
import { STLLoaderService } from '../../core/services/STLLoaderService';
import { FileSystemService } from '../../core/services/FileSystemService';
import { ModelStore } from '../../data/models/ModelStore';
import { ModelIntegrationService } from '../../core/services/ModelIntegrationService';
import './stl-file-loader.css';

/**
 * STL模型数据接口
 */
interface STLModel {
  vertices: number[];
  normals: number[];
  faces: number[];
}

/**
 * STL文件加载器组件属性接口
 */
interface STLFileLoaderProps {
  /** 模型加载完成回调 */
  onModelLoad: (model: STLModel) => void;
  /** 加载错误回调 */
  onError?: (error: string) => void;
  /** 自定义样式类名 */
  className?: string;
}

/**
 * STL文件加载器组件
 * 
 * @component
 * @description 集成文件选择、加载状态和错误处理的完整STL文件加载器
 * @example
 * ```tsx
 * <STLFileLoader 
 *   onModelLoad={(model) => console.log('模型加载完成:', model)}
 *   onError={(error) => console.error('加载错误:', error)}
 * />
 * ```
 * 
 * @returns {JSX.Element} STL文件加载器组件
 */
const STLFileLoader: React.FC<STLFileLoaderProps> = ({
  onModelLoad,
  onError,
  className = ''
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  // 组件渲染日志（开发环境）
  if (process.env.NODE_ENV === 'development') {
    console.log('STLFileLoader组件渲染');
  }

  /**
   * 使用实际STL解析服务处理文件
   */
  const parseSTLFile = useCallback(async (file: File): Promise<STLModel> => {
    setIsLoading(true);
    setError(null);
    setProgress(0);

    try {
      // 创建服务实例
      const modelStore = new ModelStore();
      const stlLoaderService = new STLLoaderService();
      const fileSystemService = new FileSystemService();
      const modelIntegrationService = new ModelIntegrationService(
        modelStore,
        stlLoaderService,
        fileSystemService
      );

      // 监听进度更新
      const unsubscribe = modelStore.subscribe((state) => {
        if (state.progress !== undefined) {
          setProgress(state.progress);
        }
      });

      try {
        // 使用ModelIntegrationService加载模型
        const mesh = await modelIntegrationService.loadModelFromFile(file);
        
        // 获取转换后的STL模型数据
        const state = modelIntegrationService.getCurrentState();
        const stlModel = state.currentModel;
        
        if (!stlModel) {
          throw new Error('模型数据转换失败');
        }

        return stlModel;
      } finally {
        unsubscribe();
      }
    } catch (error) {
      throw new Error(`STL文件解析失败: ${error instanceof Error ? error.message : '未知错误'}`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * 处理文件选择
   */
  const handleFileSelect = useCallback(async (file: File) => {
    try {
      // 开发环境日志
      if (process.env.NODE_ENV === 'development') {
        console.log('选择的文件:', file.name, file.size, file.type);
      }
      
      // 使用实际的STL解析服务
      const model = await parseSTLFile(file);
      onModelLoad(model);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      setError(errorMessage);
      onError?.(errorMessage);
    }
  }, [parseSTLFile, onModelLoad, onError]);

  /**
   * 处理文件选择错误
   */
  const handleFileError = useCallback((errorMessage: string) => {
    setError(errorMessage);
    onError?.(errorMessage);
  }, [onError]);

  /**
   * 重置错误状态
   */
  const handleErrorReset = useCallback(() => {
    setError(null);
    setProgress(0);
  }, []);

  return (
    <div className={`stl-file-loader ${className}`} data-testid="stl-file-loader">
      <div className="file-loader-section">
        <FileSelector
          onFileSelect={handleFileSelect}
          onError={handleFileError}
          accept=".stl"
          buttonText="选择STL文件"
          disabled={isLoading}
        />
      </div>

      <div className="status-section">
        <LoadingIndicator
          isLoading={isLoading}
          text="正在解析STL文件..."
          progress={progress}
        />

        <ErrorDisplay
          hasError={error !== null}
          error={error || undefined}
          onReset={handleErrorReset}
        />
      </div>

      {!isLoading && !error && (
        <div className="instruction-section" data-testid="instruction-section">
          <p>请选择STL格式的心脏模型文件</p>
          <ul>
            <li>支持标准STL文件格式</li>
            <li>文件大小限制: 250MB</li>
            <li>建议使用心脏解剖模型</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default STLFileLoader;
export type { STLModel };
