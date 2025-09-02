import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import API_URL from "../../constant";

export const fetchCategories = createAsyncThunk("categoriesList", async () => {
  try {
    const response = await fetch(`${API_URL}/api/categories/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching categories:", error);
    throw error;
  }
});

const categoriesSlice = createSlice({
  name: "categories",
  initialState: {
    isLoading: false,
    data: null,
    isError: false,
  },
  extraReducers: (builder) => {
    builder.addCase(fetchCategories.pending, (state, action) => {
      state.isLoading = true;
    });
    builder.addCase(fetchCategories.fulfilled, (state, action) => {
      state.isLoading = false;
      state.data = action.payload;
    });
    builder.addCase(fetchCategories.rejected, (state, action) => {
      console.log("Error", action.error);
      state.isLoading = false;
      state.isError = true;
      state.data = null;
    });
  },
});

export default categoriesSlice.reducer;
