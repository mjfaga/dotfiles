import { ExtensionContext, TreeItem, Location, Command } from 'vscode';
export declare class LocationTreeItem extends TreeItem {
    readonly location: Location;
    constructor(ctx: ExtensionContext, location: Location);
    get description(): string;
    get command(): Command;
}
