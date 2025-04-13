import { ProgressBaseItem } from './ProgressBaseItem';
import { BaseTreeItem } from './Base';
export declare class ProgressRootItem extends ProgressBaseItem {
    get description(): string;
    get locale(): string;
    get visible(): boolean;
    get isSource(): boolean;
    get isDisplay(): boolean;
    get iconPath(): string | {
        light: string;
        dark: string;
    } | undefined;
    get contextValue(): string;
    getChildren(): Promise<BaseTreeItem[]>;
}
