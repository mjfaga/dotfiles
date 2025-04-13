// Creates an array of elements split into groups the length of size.
// If array can't be split evenly, the final chunk will be the remaining elements.
// Works similary as https://lodash.com/docs/4.17.15#chunk
Object.defineProperty(exports, "__esModule", { value: true });
exports.chunk = void 0;
var chunk = function (arr, size) {
    var chunkSize = Math.max(size, 1);
    return arr.reduce(function (chunks, element, index) {
        var chunkIndex = Math.floor(index / chunkSize);
        if (!chunks[chunkIndex]) {
            chunks[chunkIndex] = [];
        }
        chunks[chunkIndex].push(element);
        return chunks;
    }, []);
};
exports.chunk = chunk;
//# sourceMappingURL=chunk.js.map