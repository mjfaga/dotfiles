import { CustomRefactorTemplate } from '~/core/types';
export declare function resolveRefactorTemplate(arr?: (string | CustomRefactorTemplate & {
    template?: string;
})[]): CustomRefactorTemplate[];
