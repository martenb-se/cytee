import {createStore, applyMiddleware, compose} from 'redux';
import thunkMiddleware from 'redux-thunk';

import rootReducer from 'reducers/reducer'

const middlewareEnhancer = applyMiddleware(thunkMiddleware);
const composedEnhancers = compose(middlewareEnhancer);
const store = createStore(rootReducer, undefined, composedEnhancers );

export default store