"use client"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { useEffect, useState } from 'react';
import axios from 'axios';

const getTodayDate = () => {
  const today = new Date();
  const month = `0${today.getMonth() + 1}`.slice(-2);
  const day = `0${today.getDate()}`.slice(-2);
  return `${today.getFullYear()}-${month}-${day}`;
};

const AssetsGlance = () => {

  const api_url = process.env.NEXT_PUBLIC_API_URL;

  const [assetsGlance, setAssetsGlance] = useState([]);

  useEffect(() => {
    const fetchAssetsGlance = async () => {
      try {
        const userId = localStorage.getItem('user_id');
        const portfolioResponse = await axios.get(`${api_url}/portfolios/get_portfolio/${userId}`);
        const portfolioId = portfolioResponse.data.PortfolioID;

        const assetsResponse = await axios.get(`${api_url}/assets/get_all_assets_by_portfolio_id/${portfolioId}`);
        setAssetsGlance(assetsResponse.data);
      } catch (error) {
        console.error('Failed to fetch assets:', error.response?.data || error.message);
      }
    };

    fetchAssetsGlance();
  }, [api_url]);
  
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Asset Name</TableHead>
          <TableHead>Type</TableHead>
          {/* <TableHead>Description</TableHead> */}
          <TableHead>Price</TableHead>
          <TableHead>Currency</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {assetsGlance.map((asset) => (
          <TableRow key={asset.AssetID}>
            <TableCell>
              <div className="font-medium">{asset.AssetName}</div>
              <div className="hidden text-sm text-muted-foreground md:inline">
              {asset.Description}
              </div>
            </TableCell>
            <TableCell>{asset.AssetType}</TableCell>
            <TableCell>
              {asset.MarketPrice}
            </TableCell>
            <TableCell>{asset.Currency}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

const AssetsTable = () => {

  const api_url = process.env.NEXT_PUBLIC_API_URL;

  const [assets, setAssets] = useState([]);

  useEffect(() => {
    const fetchAssets = async () => {
      try {
        const userId = localStorage.getItem('user_id');
        const portfolioResponse = await axios.get(`${api_url}/portfolios/get_portfolio/${userId}`);
        const portfolioId = portfolioResponse.data.PortfolioID;

        const assetsResponse = await axios.get(`${api_url}/assets/get_all_assets_by_portfolio_id/${portfolioId}`);
        setAssets(assetsResponse.data);
      } catch (error) {
        console.error('Failed to fetch assets:', error.response?.data || error.message);
      }
    };

    fetchAssets();
  }, [api_url]);

  const [showForm, setShowForm] = useState(false);
  const [assetName, setAssetName] = useState('');
  const [assetType, setAssetType] = useState('');
  const [description, setDescription] = useState('');
  const [marketPrice, setMarketPrice] = useState('');
  const [currency, setCurrency] = useState('');

  const handleAdd = async (event) => {
    event.preventDefault();
  
    try {
      // Step 1: Create Asset
      const createAssetResponse = await axios.post(`${api_url}/assets/create_asset`, {
        asset_name: assetName,
        asset_type: assetType,
        description: description,
        market_price: marketPrice,
        currency: currency,
      });
  
      const newAssetId = createAssetResponse.data.asset_id;
  
      if (createAssetResponse.status === 200) {
        // Step 2: Fetch portfolio ID
        const userId = localStorage.getItem('user_id');
        const portfolioResponse = await axios.get(`${api_url}/portfolios/get_portfolio/${userId}`);
        const portfolioId = portfolioResponse.data.PortfolioID;
  
        // Step 3: Create Holding
        const creationDate = getTodayDate();
        const createHoldingResponse = await axios.post(`${api_url}/holdings/create_holding`, {
          portfolio_id: portfolioId,
          asset_id: newAssetId,
          quantity: 1, // Assuming initial quantity is 1, adjust as needed
          purchase_price: marketPrice,
          purchase_date: creationDate,
        });
  
        if (createHoldingResponse.status === 200) {
          // Step 4: Create "Buy" transaction for the new asset
          const addTransactionResponse = await axios.post(`${api_url}/transaction/add_transaction`, {
            portfolio_id: portfolioId,
            asset_id: newAssetId,
            transaction_type: "Buy",
            quantity: 1,
            transaction_price: marketPrice,
            transaction_date: creationDate,
          });
  
          if (addTransactionResponse.status === 200) {
            console.log(addTransactionResponse.data.message);
            // Optionally, refresh the assets list or show a success message
          } else {
            throw new Error('Failed to create transaction');
          }
        } else {
          throw new Error('Failed to create holding');
        }
  
        // Reset form fields after successful asset, holding, and transaction creation
        setShowForm(false);
        setAssetName('');
        setAssetType('');
        setDescription('');
        setMarketPrice('');
        setCurrency('');
      } else {
        throw new Error('Asset creation was not successful');
      }
    } catch (error) {
      console.error('Asset creation, holding creation, or transaction failed:', error.response?.data || error.message);
    }
  };

  const [newPrice, setNewPrice] = useState({}); // State to store new prices for each asset
  const [errorMessages, setErrorMessages] = useState({}); // State to store error messages

  const handleBuy = async (asset) => {

    const buyPrice = parseFloat(newPrice[asset.AssetID]);
    if (!buyPrice) {
      setErrorMessages({ ...errorMessages, [asset.AssetID]: 'Please enter a new price' });
      return;
    }

    try {
      // Step 1: Fetch the holding for the asset
      const holdingResponse = await axios.get(`${api_url}/holdings/get_holding_by_asset_id/${asset.AssetID}`);
      const holding = holdingResponse.data;
      const currentQuantity = holding.Quantity;
  
      // Step 2: Calculate the new average price and quantity
      const newQuantity = currentQuantity + 1;
      const newAveragePrice = (parseFloat(asset.MarketPrice * currentQuantity) + buyPrice) / newQuantity;
  
      // Step 3: Update the asset with the new average price
      await axios.put(`${api_url}/assets/update_asset/${asset.AssetID}`, {
        // Assuming you have the asset details available, otherwise, you may need to fetch them or adjust the API
        asset_name: asset.AssetName,
        asset_type: asset.AssetType,
        description: asset.Description,
        market_price: newAveragePrice,
        currency: asset.Currency,
      });
  
      // Step 4: Update the holding with the new quantity and average price
      const userId = localStorage.getItem('user_id');
      const portfolioResponse = await axios.get(`${api_url}/portfolios/get_portfolio/${userId}`);
      const portfolioId = portfolioResponse.data.PortfolioID;
      const updateHoldingResponse = await axios.put(`${api_url}/holdings/update_holding_by_asset_id/${asset.AssetID}`, {
        // Assuming you have the portfolio ID available, otherwise, you may need to fetch it
        portfolio_id: portfolioId,
        asset_id: asset.AssetID,
        quantity: newQuantity,
        purchase_price: newAveragePrice,
        purchase_date: getTodayDate(),
      });
      // Step 5: Create "Buy" transaction for the new asset
      if (updateHoldingResponse.status === 200) {
        console.log("Asset and holding updated successfully.");
        const addTransactionResponse = await axios.post(`${api_url}/transaction/add_transaction`, {
          portfolio_id: portfolioId,
          asset_id: asset.AssetID,
          transaction_type: "Buy",
          quantity: 1,
          transaction_price: buyPrice,
          transaction_date: getTodayDate(),
        });
        if (addTransactionResponse.status === 200) {
          console.log(addTransactionResponse.data.message);
          // Optionally, refresh the assets list or show a success message
        } else {
          throw new Error('Failed to create transaction');
        }
      } else {
        throw new Error('Failed to create holding');
      }
      // Step 6: Create a performance entry
      await axios.post(`${api_url}/performance/add_performance/${portfolioId}`);

      setNewPrice({ ...newPrice, [asset.AssetID]: '' });
      setErrorMessages({ ...errorMessages, [asset.AssetID]: '' });
    } catch (error) {
      console.error('Failed to update asset and holding:', error.response?.data || error.message);
    }
  };

  const handleSell = async (asset) => {

    try {
      // Step 1: Fetch the holding for the asset
      const holdingResponse = await axios.get(`${api_url}/holdings/get_holding_by_asset_id/${asset.AssetID}`);
      const holding = holdingResponse.data;
      const currentQuantity = holding.Quantity;

      if (currentQuantity <= 0) {
          console.error("No assets to sell");
          setErrorMessages({ ...errorMessages, [asset.AssetID]: 'No assets to sell' });
          return;
      }

      // Step 2: Calculate the new average price and quantity after selling one
      const newQuantity = currentQuantity - 1;
      const sellPrice = parseFloat(asset.MarketPrice);
      let newAveragePrice;

      if (newQuantity === 0) {
          newAveragePrice = 0; // If selling all assets, the new average price might be reset
      } else {
          // Calculate the average price without the sold asset if necessary
          newAveragePrice = (parseFloat(holding.PurchasePrice) * currentQuantity - sellPrice) / newQuantity;
      }

      // Step 3: Update the asset with the new average price
      // If your application requires updating the asset after a sale, include this step

      // Step 4: Update the holding with the new quantity and average price
      const userId = localStorage.getItem('user_id');
      const portfolioResponse = await axios.get(`${api_url}/portfolios/get_portfolio/${userId}`);
      const portfolioId = portfolioResponse.data.PortfolioID;
      console.log(portfolioId);

      const updateHoldingResponse = await axios.put(`${api_url}/holdings/update_holding_by_asset_id/${asset.AssetID}`, {
          portfolio_id: portfolioId,
          asset_id: asset.AssetID,
          quantity: newQuantity,
          purchase_price: holding.PurchasePrice,
          purchase_date: holding.PurchaseDate,
      });
      // Step 5: Create "Buy" transaction for the new asset
      if (updateHoldingResponse.status === 200) {
        console.log("Asset and holding updated successfully.");
        const addTransactionResponse = await axios.post(`${api_url}/transaction/add_transaction`, {
          portfolio_id: portfolioId,
          asset_id: asset.AssetID,
          transaction_type: "Sell",
          quantity: 1,
          transaction_price: sellPrice,
          transaction_date: getTodayDate(),
        });
        if (addTransactionResponse.status === 200) {
          console.log(addTransactionResponse.data.message);
          // Optionally, refresh the assets list or show a success message
        } else {
          throw new Error('Failed to create transaction');
        }
      } else {
        throw new Error('Failed to create holding');
      }
      // Step 6: Create a performance entry
      await axios.post(`${api_url}/performance/add_performance/${portfolioId}`);

      // Optionally, refresh the assets list or show a success message
      console.log("Asset and holding updated successfully after sale.");

      // Reset any relevant state
      setErrorMessages({ ...errorMessages, [asset.AssetID]: '' });
    } catch (error) {
      console.error('Failed to update holding after selling:', error.response?.data || error.message);
    }
  };
  
  return (
    <>
      <Button onClick={() => setShowForm(!showForm)}>
        {showForm ? "Close" : "Add Asset"}
      </Button>
      {showForm && (
        <div className="mb-10">
          <form onSubmit={handleAdd}>
            <Input id="assetName" type="text" placeholder="Asset Name" required value={assetName} onChange={(e) => setAssetName(e.target.value)} />
            <Select value={assetType} onValueChange={setAssetType}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Asset Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Stock">Stock</SelectItem>
                <SelectItem value="Bond">Bond</SelectItem>
                <SelectItem value="ETF">ETF</SelectItem>
                {/* Add more asset types as needed */}
              </SelectContent>
            </Select>
            <Input id="description" type="text" placeholder="Description" required value={description} onChange={(e) => setDescription(e.target.value)} />
            <Input id="marketPrice" type="number" placeholder="Market Price" required value={marketPrice} onChange={(e) => setMarketPrice(e.target.value)} />
            <Select value={currency} onValueChange={setCurrency}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Currency" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="USD">USD</SelectItem>
                <SelectItem value="CAD">CAD</SelectItem>
                <SelectItem value="EUR">EUR</SelectItem>
                {/* Add more currencies as needed */}
              </SelectContent>
            </Select>
            <Button type="submit">Submit</Button>
          </form>
        </div>
      )}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Asset Name</TableHead>
            <TableHead>Type</TableHead>
            {/* <TableHead>Description</TableHead> */}
            <TableHead>Price</TableHead>
            <TableHead>Currency</TableHead>
            <TableHead>+1 Buy Price</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {assets.map((asset) => (
            <TableRow key={asset.AssetID}>
              <TableCell>
                <div className="font-medium">{asset.AssetName}</div>
                <div className="hidden text-sm text-muted-foreground md:inline">
                {asset.Description}
                </div>
              </TableCell>
              <TableCell>{asset.AssetType}</TableCell>
              <TableCell>
                {asset.MarketPrice}
              </TableCell>
              <TableCell>{asset.Currency}</TableCell>
              <TableCell>
                <Input
                  type="number"
                  value={newPrice[asset.AssetID] || ''}
                  onChange={(e) => setNewPrice({ ...newPrice, [asset.AssetID]: e.target.value })}
                />
                {errorMessages[asset.AssetID] && <div className="text-red-600">{errorMessages[asset.AssetID]}</div>}
              </TableCell>
              <TableCell>
                <Button onClick={() => handleBuy(asset)}>
                  +1
                </Button>
                <Button onClick={() => handleSell(asset)}>
                  -1
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </>
  );
};

export {AssetsGlance, AssetsTable};