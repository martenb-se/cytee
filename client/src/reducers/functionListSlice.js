import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import {getProjectFunctions} from '../util/api';

const initialState = {
    status: "",
    error: "",
    list: []
}

export const fetchFunctionList = createAsyncThunk('functionList/fetchFunctionList', async (pathToProject) => {
    return await getProjectFunctions(pathToProject);
})

export const functionListSlice = createSlice({
    name: 'functionList',
    initialState: initialState,
    reducers: {
        setFunctionList: (state, action) => {
          state.functionList.list = action.payload;
        }
    },
    extraReducers(builder) {
        builder
            .addCase(fetchFunctionList.pending, (state, action) => {
                state.status = 'loading';
            })
            .addCase(fetchFunctionList.fulfilled, (state, action) => {
                state.status = 'succeeded';
                state.list = action.payload.projectFunctions;
            })
            .addCase(fetchFunctionList.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.error.message;
            })
    }
})

export const selectFunctionList = state => state.functionList.list;
export const selectFunctionListLoading = state => state.functionList.status;
export const selectFunctionListError = state => state.functionList.error;

export default functionListSlice.reducer;