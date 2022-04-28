import {createSlice, createAsyncThunk} from "@reduxjs/toolkit";
import cloneDeep from 'lodash/cloneDeep';
import {saveTest, updateTest, deleteTest} from "../util/api";

const initialState = {
    status: "",
    error: "",
    test: {},
};


export const saveTestInfo = createAsyncThunk('activeTest/saveTestInfo', async (testData) => {
    return await saveTest(testData.pathToProject, testData.fileId, testData.functionId, testData.testModule);

});

export const updateTestInfo = createAsyncThunk('activeTest/updateTestInfo', async (testData) => {
    return await updateTest(testData.testId, testData.testModule, testData.customName);

});

export const deleteTestInfo = createAsyncThunk('activeTest/deleteTestInfo', async (testId) => {
    return await deleteTest(testId);
})

export const activeTestSlice = createSlice({
    name: 'activeTest',
    initialState: initialState,
    reducers: {
        setActiveTest: (state, action) => {
            console.log(action);
            state.test = cloneDeep(action.payload);
        },
        setActiveTestEmpty: (state, action) => {
            state.test = {}
        },
    },
    extraReducers(builder) {
        builder
            .addCase(saveTestInfo.pending, (state, action) => {
                state.status = 'loading';
            })
            .addCase(saveTestInfo.fulfilled, (state, action) => {
                state.status = 'succeeded';
            })
            .addCase(saveTestInfo.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.error.message;
            })
            .addCase(updateTestInfo.pending, (state, action) => {
                state.status = 'loading';
            })
            .addCase(updateTestInfo.fulfilled, (state, action) => {
                state.status = 'succeeded';
            })
            .addCase(updateTestInfo.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.error.message;
            })
            .addCase(deleteTestInfo.pending, (state, action) => {
                state.status = 'loading';
            })
            .addCase(deleteTestInfo.fulfilled, (state, action) => {
                state.status = 'succeeded';
            })
            .addCase(deleteTestInfo.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.error.message;
            })
    }
});

export const selectActiveTest = state => state.activeTest.test;
export const selectActiveTestLoadingState = state => state.activeTest.status;
export const selectActiveTestError = state => state.activeTest.error;
export const {setActiveTest, setActiveTestEmpty} = activeTestSlice.actions;
export default activeTestSlice.reducer;