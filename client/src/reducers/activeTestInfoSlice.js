import {createSlice, createAsyncThunk} from "@reduxjs/toolkit";
import cloneDeep from 'lodash/cloneDeep';
import {saveTest, updateTest, deleteTest} from "../util/api";

const initialState = {
    status: "",
    error: "",
    test: {},
    unsavedTest: {},
};

export const saveTestInfo = createAsyncThunk('activeTest/saveTestInfo', async ({}, {getState}) => {
    const unsavedData = getState().activeTest.unsavedTest;
    const pathToProject = getState().project.path;
    const functionInfo = getState().activeFunction.activeFunction;
    const testInfoState = {
        pathToProject: pathToProject,
        fileId: functionInfo.fileId,
        functionId: functionInfo.functionId,
        moduleData: cloneDeep(unsavedData.moduleData),
        customName: unsavedData.customName
    }
     let status = await saveTest(
        testInfoState.pathToProject,
        testInfoState.fileId,
        testInfoState.functionId,
        testInfoState.moduleData,
        testInfoState.customName
    );
    testInfoState._id = status.testId;
    return testInfoState;

})
export const updateTestInfo = createAsyncThunk('activeTest/updateTestInfo', async ({}, {getState}) => {
    const testInfoState = cloneDeep(getState().activeTest.unsavedTest);
    await updateTest(testInfoState._id, testInfoState.moduleData, testInfoState.customName);
    return testInfoState;
});

export const deleteTestInfo = createAsyncThunk('activeTest/deleteTestInfo', async ({},{getState}) => {
    return await deleteTest(getState().activeTest.test._id);
})

export const activeTestSlice = createSlice({
    name: 'activeTest',
    initialState: initialState,
    reducers: {
        setActiveUnsavedTest: (state, action) => {
            state.unsavedTest = cloneDeep(action.payload);
        },
        setActiveTest: (state, action) => {
            state.test = cloneDeep(action.payload);
        },
        addModuleData: (state, action) => {
            const addUnsavedTestState = cloneDeep(state.unsavedTest.moduleData);
            const functionInfo = action.payload.activeFunction;

            switch (action.payload.moduleName) {
                case 'argumentList':
                    const funcArguments =  parseFunction(functionInfo.arguments)
                    const moduleArguments = [];
                    for (const argumentData of funcArguments) {
                        const subFunctionName = argumentData.functionName;
                        for (const argument of argumentData['arguments']) {
                            moduleArguments.push({
                                subFunctionName: subFunctionName,
                                argument: argument,
                                type: 'undefined',
                            });
                        }
                    }

                    addUnsavedTestState.argumentList = moduleArguments;
                    break;
                case 'returnValue':
                    addUnsavedTestState.returnValue = {type: 'undefined'};
                    break;
                case 'exception':
                    addUnsavedTestState.exception = {value: ''};
                    break;
                default:
                    break;
            }

            state.unsavedTest.moduleData = addUnsavedTestState;
        },
        removeModuleData: (state, action) => {
            const removedModuleState = cloneDeep(state.unsavedTest.moduleData);
            delete removedModuleState[action.payload];
            state.unsavedTest.moduleData = removedModuleState;
        },
        updateArgumentList: (state, action) => {
            const newStateClone = cloneDeep(state.unsavedTest.moduleData.argumentList);
            const argumentIndex = newStateClone.findIndex(
                (argument) => (
                    (argument.argument === action.payload.argument) &&
                    (argument.subFunctionName === action.payload.subFunctionName)
                )
            );
            newStateClone.splice(argumentIndex, 1, action.payload);
            state.unsavedTest.moduleData.argumentList = newStateClone
        },
        updateReturnValue: (state, action) => {
            state.unsavedTest.moduleData.returnValue = action.payload;
        },
        updateUnsavedCustomName: (state, action) => {
            state.unsavedTest.customName = cloneDeep(action.payload);
        },
        discardUnsavedChanges: (state) => {
            state.unsavedTest = cloneDeep(state.test);
        },
        updateException: (state, action) =>{
            state.unsavedTest.moduleData.exception.value = action.payload;
        }
    },
    extraReducers(builder) {
        builder
            .addCase(saveTestInfo.pending, (state) => {
                state.status = 'loading';
            })
            .addCase(saveTestInfo.fulfilled, (state, action) => {
                state.status = 'succeeded';
                state.test = action.payload;
            })
            .addCase(saveTestInfo.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.error.message;
            })
            .addCase(updateTestInfo.pending, (state) => {
                state.status = 'loading';
            })
            .addCase(updateTestInfo.fulfilled, (state, action) => {
                state.status = 'succeeded';
                state.test = action.payload;
            })
            .addCase(updateTestInfo.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.error.message;
            })
            .addCase(deleteTestInfo.pending, (state) => {
                state.status = 'loading';
            })
            .addCase(deleteTestInfo.fulfilled, (state) => {
                state.status = 'succeeded';
            })
            .addCase(deleteTestInfo.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.error.message;
            })
    }
});

export const selectActiveTest = state => state.activeTest.test;
export const selectUnsavedActiveTest = state => state.activeTest.unsavedTest;
export const selectActiveTestLoadingState = state => state.activeTest.status;

export const {
    setActiveUnsavedTest,
    setActiveTest,
    addModuleData,
    removeModuleData,
    updateArgumentList,
    updateReturnValue,
    updateException,
    updateUnsavedCustomName,
    discardUnsavedChanges} = activeTestSlice.actions;
export default activeTestSlice.reducer;