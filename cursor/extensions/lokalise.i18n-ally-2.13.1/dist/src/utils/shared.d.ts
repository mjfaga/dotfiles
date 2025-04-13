import { ReviewComment } from '~/core/types';
export declare function getAvatarFromEmail(email?: string): string;
export declare function getCommentState(comments: ReviewComment[]): "approve" | "request_change" | "comment" | "conflict" | undefined;
