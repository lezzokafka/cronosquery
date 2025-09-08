#!/usr/bin/env python3
"""
Cronos Chain Data Query CLI Tool

This CLI tool allows users to interactively query data from both Cronos EVM and POS chains
using their respective REST APIs:
- Cronos EVM: https://rest.cronos.org/
- Cronos POS: https://rest.mainnet.crypto.org/

Based on the Cosmos SDK modules available in KAVA swagger documentation.

Implements GitHub Issue #2: Add support for Cronos POS
https://github.com/lezzokafka/cronosquery/issues/2
"""

import requests
import json
import sys
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin


class CronosCLI:
    def __init__(self, base_url: str = "https://rest.cronos.org/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Define available chains (EVM first as default)
        self.chains = {
            "evm": {
                "name": "Cronos EVM Chain",
                "base_url": "https://rest.cronos.org/",
                "description": "Cronos EVM-compatible chain for smart contracts and DeFi (DEFAULT)"
            },
            "pos": {
                "name": "Cronos POS Chain", 
                "base_url": "https://rest.mainnet.crypto.org/",
                "description": "Cronos Proof-of-Stake chain for Cosmos SDK modules"
            }
        }
        
        # Define available modules and their endpoints based on Cosmos SDK
        # Note: Using correct API versions based on actual Cronos implementation
        self.modules = {
            "auth": {
                "name": "Authentication & Accounts",
                "endpoints": {
                    "account": {
                        "name": "Get account details",
                        "path": "cosmos/auth/v1beta1/accounts/{address}",
                        "params": ["address"]
                    },
                    "accounts": {
                        "name": "List all accounts",
                        "path": "cosmos/auth/v1beta1/accounts",
                        "params": []
                    },
                    "params": {
                        "name": "Get auth parameters",
                        "path": "cosmos/auth/v1beta1/params",
                        "params": []
                    }
                }
            },
            "bank": {
                "name": "Bank & Balances",
                "endpoints": {
                    "balances": {
                        "name": "Get account balances",
                        "path": "cosmos/bank/v1beta1/balances/{address}",
                        "params": ["address"]
                    },
                    "balance": {
                        "name": "Get specific token balance",
                        "path": "cosmos/bank/v1beta1/balances/{address}/by_denom",
                        "params": ["address", "denom"]
                    },
                    "supply": {
                        "name": "Get total supply",
                        "path": "cosmos/bank/v1beta1/supply",
                        "params": []
                    },
                    "denom_metadata": {
                        "name": "Get token metadata",
                        "path": "cosmos/bank/v1beta1/denoms_metadata",
                        "params": []
                    }
                }
            },
            "gov": {
                "name": "Governance",
                "endpoints": {
                    "proposals": {
                        "name": "List proposals",
                        "path": "cosmos/gov/v1/proposals",
                        "params": []
                    },
                    "proposal": {
                        "name": "Get proposal details",
                        "path": "cosmos/gov/v1/proposals/{proposal_id}",
                        "params": ["proposal_id"]
                    },
                    "tally": {
                        "name": "Get proposal tally",
                        "path": "cosmos/gov/v1/proposals/{proposal_id}/tally",
                        "params": ["proposal_id"]
                    },
                    "votes": {
                        "name": "Get proposal votes",
                        "path": "cosmos/gov/v1/proposals/{proposal_id}/votes",
                        "params": ["proposal_id"]
                    },
                    "deposits": {
                        "name": "Get proposal deposits",
                        "path": "cosmos/gov/v1/proposals/{proposal_id}/deposits",
                        "params": ["proposal_id"]
                    },
                    "params": {
                        "name": "Get governance parameters",
                        "path": "cosmos/gov/v1/params",
                        "params": []
                    }
                }
            },
            "staking": {
                "name": "Staking",
                "endpoints": {
                    "validators": {
                        "name": "List validators",
                        "path": "cosmos/staking/v1beta1/validators",
                        "params": []
                    },
                    "validator": {
                        "name": "Get validator details",
                        "path": "cosmos/staking/v1beta1/validators/{validator_addr}",
                        "params": ["validator_addr"]
                    },
                    "delegations": {
                        "name": "Get delegations",
                        "path": "cosmos/staking/v1beta1/delegations/{delegator_addr}",
                        "params": ["delegator_addr"]
                    },
                    "delegation": {
                        "name": "Get specific delegation",
                        "path": "cosmos/staking/v1beta1/delegators/{delegator_addr}/validators/{validator_addr}",
                        "params": ["delegator_addr", "validator_addr"]
                    },
                    "unbonding_delegations": {
                        "name": "Get unbonding delegations",
                        "path": "cosmos/staking/v1beta1/delegators/{delegator_addr}/unbonding_delegations",
                        "params": ["delegator_addr"]
                    },
                    "redelegations": {
                        "name": "Get redelegations",
                        "path": "cosmos/staking/v1beta1/delegators/{delegator_addr}/redelegations",
                        "params": ["delegator_addr"]
                    },
                    "pool": {
                        "name": "Get staking pool",
                        "path": "cosmos/staking/v1beta1/pool",
                        "params": []
                    },
                    "params": {
                        "name": "Get staking parameters",
                        "path": "cosmos/staking/v1beta1/params",
                        "params": []
                    }
                }
            },
            "distribution": {
                "name": "Distribution & Rewards",
                "endpoints": {
                    "rewards": {
                        "name": "Get delegation rewards",
                        "path": "cosmos/distribution/v1beta1/delegators/{delegator_addr}/rewards",
                        "params": ["delegator_addr"]
                    },
                    "commission": {
                        "name": "Get validator commission",
                        "path": "cosmos/distribution/v1beta1/validators/{validator_addr}/commission",
                        "params": ["validator_addr"]
                    },
                    "community_pool": {
                        "name": "Get community pool",
                        "path": "cosmos/distribution/v1beta1/community_pool",
                        "params": []
                    },
                    "params": {
                        "name": "Get distribution parameters",
                        "path": "cosmos/distribution/v1beta1/params",
                        "params": []
                    }
                }
            },
            "slashing": {
                "name": "Slashing",
                "endpoints": {
                    "signing_infos": {
                        "name": "Get signing infos",
                        "path": "cosmos/slashing/v1beta1/signing_infos",
                        "params": []
                    },
                    "signing_info": {
                        "name": "Get validator signing info",
                        "path": "cosmos/slashing/v1beta1/signing_infos/{cons_address}",
                        "params": ["cons_address"]
                    },
                    "params": {
                        "name": "Get slashing parameters",
                        "path": "cosmos/slashing/v1beta1/params",
                        "params": []
                    }
                }
            },
            "mint": {
                "name": "Minting",
                "endpoints": {
                    "inflation": {
                        "name": "Get current inflation",
                        "path": "cosmos/mint/v1beta1/inflation",
                        "params": []
                    },
                    "annual_provisions": {
                        "name": "Get annual provisions",
                        "path": "cosmos/mint/v1beta1/annual_provisions",
                        "params": []
                    },
                    "params": {
                        "name": "Get minting parameters",
                        "path": "cosmos/mint/v1beta1/params",
                        "params": []
                    }
                }
            },
            "tendermint": {
                "name": "Tendermint Core",
                "endpoints": {
                    "node_info": {
                        "name": "Get node info",
                        "path": "cosmos/base/tendermint/v1beta1/node_info",
                        "params": []
                    },
                    "syncing": {
                        "name": "Get syncing status",
                        "path": "cosmos/base/tendermint/v1beta1/syncing",
                        "params": []
                    },
                    "latest_block": {
                        "name": "Get latest block",
                        "path": "cosmos/base/tendermint/v1beta1/blocks/latest",
                        "params": []
                    },
                    "block_by_height": {
                        "name": "Get block by height",
                        "path": "cosmos/base/tendermint/v1beta1/blocks/{height}",
                        "params": ["height"]
                    },
                    "validatorsets": {
                        "name": "Get validator sets",
                        "path": "cosmos/base/tendermint/v1beta1/validatorsets/latest",
                        "params": []
                    }
                }
            }
        }
        
        # Set default chain to EVM
        self.current_chain = "evm"
        self._update_base_url()

    def _update_base_url(self):
        """Update the base URL based on current chain selection"""
        self.base_url = self.chains[self.current_chain]["base_url"]

    def switch_chain(self, chain_key: str):
        """Switch to a different chain"""
        if chain_key in self.chains:
            self.current_chain = chain_key
            self._update_base_url()
            return True
        return False

    def get_current_chain_info(self) -> Dict[str, str]:
        """Get information about the currently selected chain"""
        return self.chains[self.current_chain]

    def make_request(self, endpoint: str, params: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """Make a request to the Cronos REST API"""
        try:
            url = urljoin(self.base_url, endpoint)
            if params:
                # Replace path parameters
                for key, value in params.items():
                    url = url.replace(f"{{{key}}}", str(value))
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error making request: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON response: {e}")
            return None

    def display_menu(self, title: str, options: Dict[str, str]) -> str:
        """Display a menu and get user selection"""
        print(f"\n🔹 {title}")
        print("=" * 50)
        
        for i, (key, value) in enumerate(options.items(), 1):
            print(f"{i}. {value}")
        
        while True:
            try:
                choice = input(f"\nSelect an option (1-{len(options)}): ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    return list(options.keys())[choice_num - 1]
                else:
                    print(f"❌ Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                sys.exit(0)

    def get_user_input(self, prompt: str, required: bool = True) -> str:
        """Get user input with validation"""
        while True:
            try:
                value = input(f"{prompt}: ").strip()
                if not value and required:
                    print("❌ This field is required")
                    continue
                return value
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                sys.exit(0)

    def format_response(self, data: Dict[str, Any]) -> str:
        """Format API response for display with better formatting"""
        if not data:
            return "No data received"
        
        # Handle different response types with better formatting
        if "tally" in data:
            return self._format_tally(data["tally"])
        elif "balances" in data:
            return self._format_balances(data)
        elif "proposals" in data:
            return self._format_proposals(data)
        elif "validators" in data:
            return self._format_validators(data)
        elif "pool" in data:
            return self._format_pool(data)
        elif "rewards" in data:
            return self._format_rewards(data)
        elif "commission" in data:
            return self._format_commission(data)
        elif "block" in data:
            return self._format_block(data)
        elif "node_info" in data:
            return self._format_node_info(data)
        else:
            # Fallback to pretty JSON for unknown formats
            return json.dumps(data, indent=2, ensure_ascii=False)

    def _format_tally(self, tally: Dict[str, Any]) -> str:
        """Format governance proposal tally"""
        result = "🗳️  PROPOSAL TALLY RESULTS\n"
        result += "=" * 40 + "\n"
        
        yes_count = int(tally.get("yes_count", "0"))
        no_count = int(tally.get("no_count", "0"))
        abstain_count = int(tally.get("abstain_count", "0"))
        veto_count = int(tally.get("no_with_veto_count", "0"))
        
        total = yes_count + no_count + abstain_count + veto_count
        
        if total > 0:
            yes_pct = (yes_count / total) * 100
            no_pct = (no_count / total) * 100
            abstain_pct = (abstain_count / total) * 100
            veto_pct = (veto_count / total) * 100
            
            result += f"✅ Yes:     {yes_count:,} ({yes_pct:.1f}%)\n"
            result += f"❌ No:      {no_count:,} ({no_pct:.1f}%)\n"
            result += f"⏸️  Abstain: {abstain_count:,} ({abstain_pct:.1f}%)\n"
            result += f"🚫 Veto:    {veto_count:,} ({veto_pct:.1f}%)\n"
            result += f"\n📊 Total Votes: {total:,}"
        else:
            result += "No votes cast yet"
        
        return result

    def _format_balances(self, data: Dict[str, Any]) -> str:
        """Format account balances"""
        result = "💰 ACCOUNT BALANCES\n"
        result += "=" * 30 + "\n"
        
        balances = data.get("balances", [])
        if not balances:
            return result + "No balances found"
        
        for balance in balances:
            denom = balance.get("denom", "unknown")
            amount = balance.get("amount", "0")
            
            # Format large numbers
            try:
                amount_num = int(amount)
                if amount_num > 1000000:
                    amount_str = f"{amount_num:,}"
                else:
                    amount_str = str(amount_num)
            except:
                amount_str = amount
            
            result += f"🪙 {denom}: {amount_str}\n"
        
        return result

    def _format_proposals(self, data: Dict[str, Any]) -> str:
        """Format governance proposals list"""
        result = "📋 GOVERNANCE PROPOSALS\n"
        result += "=" * 35 + "\n"
        
        proposals = data.get("proposals", [])
        if not proposals:
            return result + "No proposals found"
        
        for proposal in proposals[:5]:  # Show first 5
            prop_id = proposal.get("id", "unknown")
            status = proposal.get("status", "unknown")
            
            # Clean up status
            status_clean = status.replace("PROPOSAL_STATUS_", "").title()
            
            result += f"📄 Proposal #{prop_id}: {status_clean}\n"
        
        if len(proposals) > 5:
            result += f"... and {len(proposals) - 5} more proposals"
        
        return result

    def _format_validators(self, data: Dict[str, Any]) -> str:
        """Format validators list"""
        result = "⚡ VALIDATORS\n"
        result += "=" * 20 + "\n"
        
        validators = data.get("validators", [])
        if not validators:
            return result + "No validators found"
        
        # Show active validators first
        active_validators = [v for v in validators if v.get("status") == "BOND_STATUS_BONDED"]
        
        result += f"🟢 Active Validators: {len(active_validators)}\n"
        result += f"📊 Total Validators: {len(validators)}\n\n"
        
        # Show top 3 active validators
        for i, validator in enumerate(active_validators[:3]):
            moniker = validator.get("description", {}).get("moniker", "Unknown")
            tokens = validator.get("tokens", "0")
            
            try:
                tokens_num = int(tokens)
                if tokens_num > 1000000:
                    tokens_str = f"{tokens_num:,}"
                else:
                    tokens_str = str(tokens_num)
            except:
                tokens_str = tokens
            
            result += f"{i+1}. {moniker} - {tokens_str} tokens\n"
        
        return result

    def _format_pool(self, data: Dict[str, Any]) -> str:
        """Format staking pool info"""
        result = "🏊 STAKING POOL\n"
        result += "=" * 20 + "\n"
        
        pool = data.get("pool", {})
        bonded_tokens = pool.get("bonded_tokens", "0")
        not_bonded_tokens = pool.get("not_bonded_tokens", "0")
        
        try:
            bonded_num = int(bonded_tokens)
            not_bonded_num = int(not_bonded_tokens)
            total = bonded_num + not_bonded_num
            
            result += f"🔒 Bonded:     {bonded_num:,}\n"
            result += f"🔓 Unbonded:   {not_bonded_num:,}\n"
            result += f"📊 Total:      {total:,}\n"
            
            if total > 0:
                bonded_pct = (bonded_num / total) * 100
                result += f"📈 Bonded %:   {bonded_pct:.1f}%"
        except:
            result += f"🔒 Bonded:     {bonded_tokens}\n"
            result += f"🔓 Unbonded:   {not_bonded_tokens}"
        
        return result

    def _format_rewards(self, data: Dict[str, Any]) -> str:
        """Format delegation rewards"""
        result = "🎁 DELEGATION REWARDS\n"
        result += "=" * 25 + "\n"
        
        rewards = data.get("rewards", [])
        total = data.get("total", [])
        
        if total:
            for reward in total:
                denom = reward.get("denom", "unknown")
                amount = reward.get("amount", "0")
                result += f"🪙 {denom}: {amount}\n"
        else:
            result += "No rewards available"
        
        return result

    def _format_commission(self, data: Dict[str, Any]) -> str:
        """Format validator commission"""
        result = "💼 VALIDATOR COMMISSION\n"
        result += "=" * 30 + "\n"
        
        commission = data.get("commission", {})
        commission_amount = commission.get("commission", [])
        
        if commission_amount:
            for comm in commission_amount:
                denom = comm.get("denom", "unknown")
                amount = comm.get("amount", "0")
                result += f"🪙 {denom}: {amount}\n"
        else:
            result += "No commission data"
        
        return result

    def _format_block(self, data: Dict[str, Any]) -> str:
        """Format block information"""
        result = "🧱 BLOCK INFORMATION\n"
        result += "=" * 25 + "\n"
        
        block = data.get("block", {})
        header = block.get("header", {})
        
        height = header.get("height", "unknown")
        time = header.get("time", "unknown")
        proposer = header.get("proposer_address", "unknown")
        
        result += f"📏 Height:    {height}\n"
        result += f"⏰ Time:      {time}\n"
        result += f"👤 Proposer:  {proposer[:20]}..."
        
        return result

    def _format_node_info(self, data: Dict[str, Any]) -> str:
        """Format node information"""
        result = "🖥️  NODE INFORMATION\n"
        result += "=" * 25 + "\n"
        
        node_info = data.get("node_info", {})
        application_version = node_info.get("application_version", {})
        
        version = application_version.get("version", "unknown")
        name = application_version.get("name", "unknown")
        
        # Get current chain name
        chain_name = self.get_current_chain_info()["name"]
        
        result += f"📦 Name:    {name}\n"
        result += f"🏷️  Version: {version}\n"
        result += f"🌐 Network: {chain_name}"
        
        return result

    def run(self):
        """Main CLI loop"""
        print("🚀 Welcome to Cronos Chain Data Query CLI")
        print("=" * 50)
        print("This tool allows you to query data from Cronos EVM and POS chains")
        
        # Step 1: Select chain (with EVM as default)
        chain_options = {}
        for key, value in self.chains.items():
            if key == "evm":
                chain_options[key] = f"⭐ {value['name']} - {value['description']}"
            else:
                chain_options[key] = f"   {value['name']} - {value['description']}"
        
        selected_chain = self.display_menu("Which chain would you like to query? (EVM is recommended)", chain_options)
        
        if self.switch_chain(selected_chain):
            chain_info = self.get_current_chain_info()
            print(f"\n✅ Selected: {chain_info['name']}")
            print(f"🌐 Base URL: {self.base_url}")
        else:
            print("❌ Invalid chain selection")
            return
        
        while True:
            try:
                # Step 2: Select module
                module_options = {key: value["name"] for key, value in self.modules.items()}
                selected_module = self.display_menu("Which module would you like to check?", module_options)
                
                # Step 3: Select endpoint within module
                endpoint_options = {key: value["name"] for key, value in self.modules[selected_module]["endpoints"].items()}
                selected_endpoint = self.display_menu(
                    f"What would you like to check in {self.modules[selected_module]['name']}?", 
                    endpoint_options
                )
                
                # Step 4: Get required parameters
                endpoint_info = self.modules[selected_module]["endpoints"][selected_endpoint]
                params = {}
                
                for param in endpoint_info["params"]:
                    if param == "address":
                        params[param] = self.get_user_input("Enter address")
                    elif param == "proposal_id":
                        params[param] = self.get_user_input("Enter proposal number")
                    elif param == "validator_addr":
                        params[param] = self.get_user_input("Enter validator address")
                    elif param == "delegator_addr":
                        params[param] = self.get_user_input("Enter delegator address")
                    elif param == "cons_address":
                        params[param] = self.get_user_input("Enter consensus address")
                    elif param == "height":
                        params[param] = self.get_user_input("Enter block height")
                    elif param == "denom":
                        params[param] = self.get_user_input("Enter token denomination")
                    else:
                        params[param] = self.get_user_input(f"Enter {param}")
                
                # Step 5: Make request and display result
                print(f"\n🔄 Making request to {endpoint_info['path']}...")
                result = self.make_request(endpoint_info["path"], params)
                
                if result:
                    print("\n✅ Result:")
                    print("-" * 50)
                    print(self.format_response(result))
                else:
                    print("❌ Failed to retrieve data")
                
                # Ask if user wants to continue or switch chains
                print(f"\nCurrent chain: {self.get_current_chain_info()['name']}")
                continue_choice = input("\nOptions: (q)uery again, (s)witch chain, (e)xit: ").strip().lower()
                if continue_choice in ['e', 'exit']:
                    print("👋 Goodbye!")
                    break
                elif continue_choice in ['s', 'switch']:
                    # Switch chain
                    chain_options = {}
                    for key, value in self.chains.items():
                        if key == "evm":
                            chain_options[key] = f"⭐ {value['name']} - {value['description']}"
                        else:
                            chain_options[key] = f"   {value['name']} - {value['description']}"
                    
                    selected_chain = self.display_menu("Which chain would you like to query? (EVM is recommended)", chain_options)
                    
                    if self.switch_chain(selected_chain):
                        chain_info = self.get_current_chain_info()
                        print(f"\n✅ Switched to: {chain_info['name']}")
                        print(f"🌐 Base URL: {self.base_url}")
                    else:
                        print("❌ Invalid chain selection")
                elif continue_choice not in ['q', 'query', 'y', 'yes', '']:
                    print("👋 Goodbye!")
                    break
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                continue


def main():
    """Main entry point"""
    cli = CronosCLI()
    cli.run()


if __name__ == "__main__":
    main()