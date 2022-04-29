import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import {getProjectTest} from '../util/api';

const initialState = {
    status: "",
    error: "",
    list: []
}

export const fetchTestList = createAsyncThunk('testList/fetchTestList', async (pathToProject) => {
    return await getProjectTest(pathToProject);
})

export const testListSlice = createSlice({
    name: 'testList',
    initialState: initialState,
    reducers: {
        setTestList: (state, action) => {
            state.testList.list = action.payload;
        }
    },
    extraReducers(builder) {
        builder
            .addCase(fetchTestList.pending, (state, action) => {
                state.status = 'loading';
            })
            .addCase(fetchTestList.fulfilled, (state, action) => {
                state.status = 'succeeded';
                state.list = action.payload.projectTests;
            })
            .addCase(fetchTestList.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.error.message;
            })
    }

})

export const selectTestList = state => state.testList.list;
export const selectTestListLoading = state => state.testList.status;
export const selectTestListError = state => state.testList.error;

export default testListSlice.reducer;