import { Vector3 } from '../geometry/index';

/**
 * 切面可视化配置接口
 */
export interface VisualizationConfig {
  visible: boolean;
  lineWidth: number;
  color: string;
  opacity: number;
  highlight: boolean;
}

/**
 * 可视化选项接口
 */
export interface VisualizationOptions {
  color?: string;
  lineWidth?: number;
  opacity?: number;
  highlight?: boolean;
  highlightColor?: string;
}

/**
 * 切面可视化服务
 * 负责处理切面轮廓的可视化配置和显示
 */
export class SectionVisualizationService {
  private defaultConfig: VisualizationConfig = {
    visible: true,
    lineWidth: 2,
    color: '#00ff00',
    opacity: 1.0,
    highlight: false
  };

  /**
   * 获取切面可视化配置
   * @param intersectionLines 切面交线数据
   * @param options 可视化选项
   * @returns 可视化配置
   */
  getVisualizationConfig(
    intersectionLines: Vector3[][],
    options: VisualizationOptions = {}
  ): VisualizationConfig {
    // 处理空交线数据
    if (!intersectionLines || intersectionLines.length === 0) {
      return {
        ...this.defaultConfig,
        visible: false,
        lineWidth: 0
      };
    }

    // 处理无效交线数据格式
    const validLines = intersectionLines.filter(line => 
      Array.isArray(line) && line.length === 2 && 
      line[0] instanceof Vector3 && line[1] instanceof Vector3
    );

    if (validLines.length === 0) {
      return {
        ...this.defaultConfig,
        visible: false
      };
    }

    // 构建基础配置
    const config: VisualizationConfig = {
      ...this.defaultConfig,
      visible: true
    };

    // 应用自定义选项
    if (options.color !== undefined) {
      config.color = this.isValidColor(options.color) ? options.color : this.defaultConfig.color;
    }

    if (options.lineWidth !== undefined) {
      config.lineWidth = Math.max(0, options.lineWidth); // 确保线宽非负
    }

    if (options.opacity !== undefined) {
      config.opacity = Math.max(0, Math.min(1, options.opacity));
    }

    // 处理高亮显示
    if (options.highlight) {
      config.highlight = true;
      config.lineWidth = Math.max(config.lineWidth, 3); // 高亮时最小线宽为3
      
      if (options.highlightColor && this.isValidColor(options.highlightColor)) {
        config.color = options.highlightColor;
      } else {
        config.color = '#ffff00'; // 默认高亮颜色为黄色
      }
    }

    return config;
  }

  /**
   * 验证颜色格式
   * @param color 颜色值
   * @returns 是否为有效颜色格式
   */
  private isValidColor(color: string): boolean {
    return /^#[0-9a-fA-F]{6}$/.test(color);
  }

  /**
   * 获取默认配置
   * @returns 默认可视化配置
   */
  getDefaultConfig(): VisualizationConfig {
    return { ...this.defaultConfig };
  }

  /**
   * 设置默认配置
   * @param config 新的默认配置
   */
  setDefaultConfig(config: Partial<VisualizationConfig>): void {
    this.defaultConfig = {
      ...this.defaultConfig,
      ...config
    };
  }
}
