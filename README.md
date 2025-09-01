# CronosQuery ⭐

A simple command-line interface for querying data from the Cronos EVM chain using the REST API at `https://rest.cronos.org/`.

## Features

- Interactive module selection based on Cosmos SDK modules
- Support for all major Cosmos SDK modules:
  - **Authentication & Accounts** - Query account information
  - **Bank & Balances** - Check token balances and supply
  - **Governance** - View proposals, votes, and tallies
  - **Staking** - Query validators, delegations, and staking pool
  - **Distribution & Rewards** - Check rewards and commission
  - **Slashing** - View slashing information
  - **Minting** - Check inflation and annual provisions
  - **Tendermint Core** - Query blocks, validators, and node info

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the CLI tool:
```bash
python cronosquery.py
```

The tool will guide you through an interactive process:

1. **Select Module**: Choose which Cosmos SDK module you want to query
2. **Select Endpoint**: Choose the specific endpoint within that module
3. **Enter Parameters**: Provide any required parameters (addresses, IDs, etc.)
4. **View Results**: See the formatted JSON response

## Example Usage

### Querying a Governance Proposal Tally

1. Run `python cronosquery.py`
2. Select "Governance" module
3. Select "Get proposal tally" endpoint
4. Enter proposal number (e.g., "22")
5. View the tally results

This will query: `https://rest.cronos.org/cosmos/gov/v1beta1/proposals/22/tally`

### Checking Account Balances

1. Select "Bank & Balances" module
2. Select "Get account balances" endpoint
3. Enter the account address
4. View all token balances for that account

## Available Modules

### Authentication & Accounts (`auth`)
- Get account details by address
- List all accounts
- Get authentication parameters

### Bank & Balances (`bank`)
- Get account balances
- Get specific token balance
- Get total supply
- Get token metadata

### Governance (`gov`)
- List proposals
- Get proposal details
- Get proposal tally (voting results)
- Get proposal votes
- Get proposal deposits
- Get governance parameters

### Staking (`staking`)
- List validators
- Get validator details
- Get delegations
- Get specific delegation
- Get unbonding delegations
- Get redelegations
- Get staking pool
- Get staking parameters

### Distribution & Rewards (`distribution`)
- Get delegation rewards
- Get validator commission
- Get community pool
- Get distribution parameters

### Slashing (`slashing`)
- Get signing infos
- Get validator signing info
- Get slashing parameters

### Minting (`mint`)
- Get current inflation
- Get annual provisions
- Get minting parameters

### Tendermint Core (`tendermint`)
- Get node info
- Get syncing status
- Get latest block
- Get block by height
- Get validator sets

## Error Handling

The CLI includes comprehensive error handling for:
- Network connectivity issues
- Invalid API responses
- Missing required parameters
- Invalid user input

## Base URL

The tool uses `https://rest.cronos.org/` as the base URL for the Cronos EVM chain REST API. This can be modified in the code if needed for different networks.

## Requirements

- Python 3.6+
- requests library

## License

This project is open source and available under the MIT License.# cronosquery
