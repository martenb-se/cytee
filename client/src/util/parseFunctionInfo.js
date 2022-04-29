

function parseFunctionArgs(args) {
    const argumentList = [];

    for (const argumentData of args) {
        switch(argumentData.type) {
            case 'Identifier':
                argumentList.push(argumentData.name);
                break;
            case 'Property':
                argumentList.push(argumentData.key.name)
                break;
            case 'ObjectPattern':
                const objRecList = parseFunctionArgs(argumentData.properties);
                argumentList.push(...objRecList);
                break;
            case 'ArrayPattern':
                const arrRecList = parseFunctionArgs(argumentData.elements);
                argumentList.push(...arrRecList);
                break;
            case 'RestElement':
                argumentList.push('RestElement');
                break;
            default:
                break;
        }
    }
    return argumentList;
}

export function parseFunction(args) {
    const fullArgumentList = [];
    for (const func of args) {
        const funcName = Object.keys(func)[0];
        const argList = parseFunctionArgs(func[funcName]);
        fullArgumentList.push({functionName: funcName, arguments: argList});
    }
    return fullArgumentList;
}