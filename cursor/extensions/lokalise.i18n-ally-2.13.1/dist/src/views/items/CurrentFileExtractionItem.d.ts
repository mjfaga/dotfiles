import { CurrentFileLocalesTreeProvider } from '../providers';
import { BaseTreeItem } from './Base';
import { HardStringDetectResultItem } from './HardStringDetectResultItem';
export declare class CurrentFileExtractionItem extends BaseTreeItem {
    readonly provider: CurrentFileLocalesTreeProvider;
    langId: string;
    constructor(provider: CurrentFileLocalesTreeProvider);
    getLabel(): string;
    get description(): string;
    get iconPath(): string | {
        light: string;
        dark: string;
    };
    getChildren(): Promise<HardStringDetectResultItem[]>;
}
