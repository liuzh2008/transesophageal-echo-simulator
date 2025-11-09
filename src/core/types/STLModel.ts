/**
 * STL模型数据结构
 * 用于表示解析后的STL模型数据
 */
export interface STLModel {
  /** 顶点数据数组 [x1, y1, z1, x2, y2, z2, ...] */
  vertices: number[];
  /** 法线数据数组 [nx1, ny1, nz1, nx2, ny2, nz2, ...] */
  normals: number[];
  /** 面索引数组 [face1_vertex1, face1_vertex2, face1_vertex3, ...] */
  faces: number[];
  /** 模型名称 */
  name?: string;
  /** 文件大小（字节） */
  fileSize?: number;
  /** 顶点数量 */
  vertexCount?: number;
  /** 面数量 */
  faceCount?: number;
}
