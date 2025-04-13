import { Framework, PackageFileType } from './base';
import CustomFramework from './custom';
export * from './base';
export declare type PackageDependencies = Partial<Record<PackageFileType, string[]>>;
export declare const frameworks: Framework[];
export declare function getFramework(id: string): Framework | undefined;
export declare function getPackageDependencies(projectUrl: string): PackageDependencies;
export declare function getEnabledFrameworks(dependencies: PackageDependencies, root: string): Framework[];
export declare function getEnabledFrameworksByIds(ids: string[], root: string): (Framework | CustomFramework)[];
