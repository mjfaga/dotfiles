import { RewriteKeySource, DataProcessContext, RewriteKeyContext } from '../core/types';
import { Framework } from './base';
import { LanguageId } from '~/utils';
declare class RubyRailsFramework extends Framework {
    id: string;
    display: string;
    detection: {
        gemfile: string[];
    };
    languageIds: LanguageId[];
    usageMatchRegex: string[];
    refactorTemplates(keypath: string): string[];
    preprocessData(data: any, context: DataProcessContext): object;
    deprocessData(data: any, context: DataProcessContext): object;
    rewriteKeys(key: string, source: RewriteKeySource, context?: RewriteKeyContext): string;
}
export default RubyRailsFramework;
