"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.handler = exports.builder = exports.describe = exports.aliases = exports.command = void 0;
const flat_1 = require("flat");
const glob_1 = __importDefault(require("glob"));
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
const util_1 = require("util");
const list_1 = require("./fails/list");
const utils_1 = require("../utils");
const debug_1 = require("debug");
const debug = debug_1.debug('vue-i18n-locale-message:commands:list');
const writeFile = util_1.promisify(fs_1.default.writeFile);
exports.command = 'list';
exports.aliases = 'lt';
exports.describe = 'List undefined fields in locale messages';
exports.builder = (args) => {
    return args
        .option('locale', {
        type: 'string',
        alias: 'l',
        describe: `the main locale of locale messages`,
        demandOption: true
    })
        .option('target', {
        type: 'string',
        alias: 't',
        describe: 'target path that locale messages file is stored, default list with the filename of target path as locale'
    })
        .option('targetPaths', {
        type: 'string',
        alias: 'T',
        describe: 'target directory paths that locale messages files is stored, Can also be specified multi paths with comma delimiter'
    })
        .option('filenameMatch', {
        type: 'string',
        alias: 'm',
        describe: `option should be accepted a regex filenames, must be specified together --targetPaths if it's directory path of locale messages`
    })
        .option('define', {
        type: 'boolean',
        alias: 'd',
        default: false,
        describe: `if there are undefined fields in the target locale messages, define them with empty string and save them`
    })
        .option('indent', {
        type: 'number',
        alias: 'i',
        default: 2,
        describe: `option for indent of locale message, if you need to adjust with --define option`
    })
        .fail(list_1.fail);
};
exports.handler = async (args) => {
    const { locale, define } = args;
    if (!args.target && !args.targetPaths) {
        // TODO: should refactor console message
        return Promise.reject(new Error('You need to specify either --target or --target-paths'));
    }
    const localeMessages = utils_1.getLocaleMessages(args);
    const flattedLocaleMessages = {};
    Object.keys(localeMessages).forEach(locale => {
        flattedLocaleMessages[locale] = flat_1.flatten(localeMessages[locale]);
    });
    const mainLocaleMessage = flattedLocaleMessages[locale];
    if (!mainLocaleMessage) {
        console.error(`Not found main '${locale}' locale message`);
        return;
    }
    let valid = true;
    Object.keys(flattedLocaleMessages).forEach(l => {
        const message = flattedLocaleMessages[l];
        if (!message) {
            console.log(`Not found '${l}' locale messages`);
            valid = false;
        }
        else {
            Object.keys(mainLocaleMessage).forEach(key => {
                if (!message[key]) {
                    console.log(`${l}: '${key}' undefined`);
                    valid = false;
                    if (define) {
                        message[key] = '';
                    }
                }
            });
        }
    });
    if (!define && !valid) {
        return Promise.reject(new list_1.LocaleMessageUndefindError('There are undefined fields in the target locale messages, you can define with --define option'));
    }
    const unflattedLocaleMessages = {};
    Object.keys(flattedLocaleMessages).forEach(locale => {
        unflattedLocaleMessages[locale] = flat_1.unflatten(flattedLocaleMessages[locale], { object: true });
    });
    await tweakLocaleMessages(unflattedLocaleMessages, args);
    return Promise.resolve();
};
async function tweakLocaleMessages(messages, args) {
    const targets = [];
    if (args.target) {
        const targetPath = utils_1.resolve(args.target);
        const parsed = path_1.default.parse(targetPath);
        const locale = parsed.name;
        targets.push({
            path: targetPath,
            locale,
            message: messages[locale]
        });
    }
    else if (args.targetPaths) {
        const filenameMatch = args.filenameMatch;
        if (!filenameMatch) {
            // TODO: should refactor console message
            throw new Error('You need to specify together --filename-match');
        }
        const targetPaths = args.targetPaths.split(',').filter(p => p);
        targetPaths.forEach(targetPath => {
            const globedPaths = glob_1.default.sync(targetPath).map(p => utils_1.resolve(p));
            globedPaths.forEach(fullPath => {
                const parsed = path_1.default.parse(fullPath);
                const re = new RegExp(filenameMatch, 'ig');
                const match = re.exec(parsed.base);
                debug('regex match', match, fullPath);
                if (match && match[1]) {
                    const locale = match[1];
                    if (args.locale !== locale) {
                        targets.push({
                            path: fullPath,
                            locale,
                            message: messages[locale]
                        });
                    }
                }
                else {
                    // TODO: should refactor console message
                    console.log(`${fullPath} is not matched with ${filenameMatch}`);
                }
            });
        });
    }
    if (args.define) {
        for (const fileInfo of targets) {
            await writeFile(fileInfo.path, JSON.stringify(fileInfo.message, null, args.indent));
        }
    }
}
exports.default = {
    command: exports.command,
    aliases: exports.aliases,
    describe: exports.describe,
    builder: exports.builder,
    handler: exports.handler
};
