import { Node } from '~/core';
export declare class NodeHelper {
    static isSource(node: Node): boolean;
    static hasFilepath(node: Node): boolean;
    static notShadowOrHasFilepath(node: Node): boolean;
    static isTranslatable(node: Node): boolean;
    static isOpenable(node: Node): boolean;
    static isEditable(node: Node): boolean;
    static splitKeypath(keypath: string): string[];
    static getPathWithoutNamespace(keypath: string, node?: Node, namespace?: string, delimiter?: string): string;
}
