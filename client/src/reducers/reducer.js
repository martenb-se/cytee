import {combineReducers} from 'redux';
import {projectReducer} from 'reducers/project/projectReducer';

export default combineReducers({project : projectReducer});