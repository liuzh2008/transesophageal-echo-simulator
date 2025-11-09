import React, { useState, useCallback } from 'react';
import FileSelector from './FileSelector';
import LoadingIndicator from './LoadingIndicator';
import ErrorDisplay from './ErrorDisplay';
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
   * 模拟STL文件解析过程
   */
  const parseSTLFile = useCallback(async (): Promise<STLModel> => {
    return new Promise((resolve, reject) => {
      setIsLoading(true);
      setError(null);
      setProgress(0);

      // 模拟解析进度
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          const newProgress = prev + Math.random() * 20;
          return newProgress >= 100 ? 100 : newProgress;
        });
      }, 200);

      // 模拟异步解析过程
      setTimeout(() => {
        clearInterval(progressInterval);
        setProgress(100);

        try {
          // 模拟随机错误（用于测试错误处理）
          const shouldFail = Math.random() < 0.3; // 30%概率失败
          if (shouldFail) {
            throw new Error('模拟STL文件解析错误：文件格式不正确');
          }

          // 这里应该调用实际的STL解析服务
          // 目前返回模拟数据
          const mockModel: STLModel = {
            vertices: [
              0, 0, 0,    // 顶点1
              1, 0, 0,    // 顶点2  
              0, 1, 0,    // 顶点3
              1, 1, 0     // 顶点4
            ],
            normals: [
              0, 0, 1,    // 法线1
              0, 0, 1,    // 法线2
              0, 0, 1,    // 法线3
              0, 0, 1     // 法线4
            ],
            faces: [
              0, 1, 2,    // 面1
              1, 3, 2     // 面2
            ]
          };

          resolve(mockModel);
        } catch (parseError) {
          reject(new Error(`STL文件解析失败: ${parseError}`));
        } finally {
          setIsLoading(false);
        }
      }, 2000);
    });
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
      
      // 这里应该调用实际的STL解析服务
      // 目前使用模拟解析
      const model = await parseSTLFile();
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
