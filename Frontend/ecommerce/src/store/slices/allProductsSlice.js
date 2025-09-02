import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import API_URL from "../../constant";

export const fetchAllProducts = createAsyncThunk("allProductsList", async (params = {}) => {
  try {
    const queryParams = new URLSearchParams();
    
    // Add category filter if provided
    if (params.category) {
      queryParams.append('category', params.category);
    }
    
    // Add search term if provided
    if (params.search) {
      queryParams.append('search', params.search);
    }
    
    // Add price range if provided
    if (params.minPrice) {
      queryParams.append('min_price', params.minPrice);
    }
    if (params.maxPrice) {
      queryParams.append('max_price', params.maxPrice);
    }
    
    const response = await fetch(`${API_URL}/api/products/?${queryParams.toString()}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching all products:", error);
    throw error;
  }
});

const allProductsSlice = createSlice({
  name: "allProducts",
  initialState: {
    isLoading: false,
    data: null,
    isError: false,
  },
  extraReducers: (builder) => {
    builder.addCase(fetchAllProducts.pending, (state, action) => {
      state.isLoading = true;
    });
    builder.addCase(fetchAllProducts.fulfilled, (state, action) => {
      state.isLoading = false;
      state.data = action.payload;
    });
    builder.addCase(fetchAllProducts.rejected, (state, action) => {
      console.log("Error", action.error);
      state.isLoading = false;
      state.isError = true;
      state.data = null;
    });
  },
});

export default allProductsSlice.reducer;
