import { KeyInDocument, RewriteKeyContext } from '../core/types';
import { ScopeRange } from '../frameworks/base';
export declare function handleRegexMatch(text: string, match: RegExpExecArray, dotEnding?: boolean, rewriteContext?: RewriteKeyContext, scopes?: ScopeRange[], namespaceDelimiters?: string[], defaultNamespace?: string, starts?: number[]): KeyInDocument | undefined;
export declare function regexFindKeys(text: string, regs: RegExp[], dotEnding?: boolean, rewriteContext?: RewriteKeyContext, scopes?: ScopeRange[], namespaceDelimiters?: string[]): KeyInDocument[];
export declare function normalizeUsageMatchRegex(reg: (string | RegExp)[]): RegExp[];
