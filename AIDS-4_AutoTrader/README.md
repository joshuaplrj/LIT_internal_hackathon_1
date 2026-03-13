# AIDS-4: AutoTrader — Reinforcement Learning for Portfolio Management

## Overview

Design a **reinforcement learning agent** for multi-asset portfolio management across 60 assets.

## Assets

| Category | Count | Examples |
|---|---|---|
| Stocks | 50 | S&P 500 subset |
| Bond ETFs | 5 | AGG, BND, TLT, IEF, SHY |
| Commodity ETFs | 3 | GLD, SLV, USO |
| Crypto | 2 | BTC, ETH |

## Environment

- **Training**: 2010–2023 daily data
- **Testing**: 2024–2025
- **Transaction cost**: 0.1%
- **Constraints**: No short selling, max 20% per asset, min 5% cash

## Task

### 1. State Representation

Design state space capturing:
- Current portfolio weights
- Market features (prices, volumes, volatility)
- Macro regime
- Sentiment indicators

### 2. Action Space

Continuous portfolio weight vector (sums to 1.0)

### 3. Reward Function

Balance:
- Return (Sharpe ratio)
- Risk (max drawdown < 15%)
- Turnover penalty
- Tail risk (CVaR 95%)

### 4. Algorithm

Implement PPO, SAC, TD3, or DDPG

### 5. Risk Management

- Position sizing by volatility
- Dynamic hedging
- Stop-loss mechanisms

## RL Environment

```python
import gym
import numpy as np

class PortfolioEnv(gym.Env):
    """Portfolio management environment"""
    
    def __init__(self, data, initial_capital=1000000):
        super().__init__()
        
        self.data = data
        self.initial_capital = initial_capital
        self.n_assets = data['returns'].shape[1]
        
        # Action space: portfolio weights
        self.action_space = gym.spaces.Box(
            low=0, high=0.2, shape=(self.n_assets + 1,),  # +1 for cash
            dtype=np.float32
        )
        
        # State space
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf,
            shape=(self.n_assets * 5 + 10,),  # Features per asset + portfolio state
            dtype=np.float32
        )
    
    def reset(self):
        """Reset environment"""
        self.current_step = 0
        self.portfolio_value = self.initial_capital
        self.weights = np.zeros(self.n_assets + 1)
        self.weights[-1] = 1.0  # All cash initially
        
        return self._get_state()
    
    def step(self, action):
        """Execute one step"""
        # Normalize action to valid weights
        action = np.clip(action, 0, 0.2)
        action = action / action.sum()
        
        # Calculate transaction costs
        turnover = np.sum(np.abs(action - self.weights))
        transaction_cost = turnover * self.portfolio_value * 0.001
        
        # Update weights
        self.weights = action
        
        # Get returns
        returns = self.data['returns'][self.current_step]
        
        # Portfolio return
        portfolio_return = np.sum(self.weights[:-1] * returns)
        
        # Update portfolio value
        self.portfolio_value *= (1 + portfolio_return)
        self.portfolio_value -= transaction_cost
        
        # Calculate reward
        reward = self._calculate_reward(portfolio_return, transaction_cost)
        
        # Next step
        self.current_step += 1
        done = self.current_step >= len(self.data['returns']) - 1
        
        return self._get_state(), reward, done, {}
    
    def _get_state(self):
        """Get current state"""
        # Market features
        market_features = []
        for i in range(self.n_assets):
            market_features.extend([
                self.data['returns'][self.current_step, i],
                self.data['volatility'][self.current_step, i],
                self.data['volume'][self.current_step, i],
                self.data['rsi'][self.current_step, i],
                self.data['macd'][self.current_step, i],
            ])
        
        # Portfolio state
        portfolio_state = [
            self.portfolio_value / self.initial_capital,
            *self.weights,
        ]
        
        return np.array(market_features + portfolio_state, dtype=np.float32)
    
    def _calculate_reward(self, portfolio_return, transaction_cost):
        """Calculate reward"""
        # Sharpe ratio component
        sharpe_reward = portfolio_return
        
        # Risk penalty
        risk_penalty = -0.1 * max(0, portfolio_return - 0.02)**2
        
        # Turnover penalty
        turnover_penalty = -0.01 * transaction_cost / self.portfolio_value
        
        return sharpe_reward + risk_penalty + turnover_penalty
```

## PPO Agent

```python
import torch
import torch.nn as nn
import torch.optim as optim

class PPOAgent:
    """Proximal Policy Optimization agent"""
    
    def __init__(self, state_dim, action_dim, lr=3e-4):
        self.actor = ActorNetwork(state_dim, action_dim)
        self.critic = CriticNetwork(state_dim)
        
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=lr)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=lr)
        
        self.clip_epsilon = 0.2
        self.entropy_coef = 0.01
    
    def select_action(self, state):
        """Select action from policy"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        
        with torch.no_grad():
            action_dist = self.actor(state_tensor)
            action = action_dist.sample()
            log_prob = action_dist.log_prob(action).sum(dim=-1)
        
        return action.squeeze().numpy(), log_prob.item()
    
    def update(self, states, actions, log_probs_old, returns, advantages):
        """Update policy using PPO"""
        states = torch.FloatTensor(states)
        actions = torch.FloatTensor(actions)
        log_probs_old = torch.FloatTensor(log_probs_old)
        returns = torch.FloatTensor(returns)
        advantages = torch.FloatTensor(advantages)
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        for _ in range(10):  # PPO epochs
            # Actor loss
            action_dist = self.actor(states)
            log_probs = action_dist.log_prob(actions).sum(dim=-1)
            
            ratio = torch.exp(log_probs - log_probs_old)
            surr1 = ratio * advantages
            surr2 = torch.clamp(ratio, 1 - self.clip_epsilon, 1 + self.clip_epsilon) * advantages
            
            actor_loss = -torch.min(surr1, surr2).mean()
            
            # Entropy bonus
            entropy = action_dist.entropy().mean()
            actor_loss -= self.entropy_coef * entropy
            
            # Critic loss
            values = self.critic(states).squeeze()
            critic_loss = nn.MSELoss()(values, returns)
            
            # Update
            self.actor_optimizer.zero_grad()
            actor_loss.backward()
            self.actor_optimizer.step()
            
            self.critic_optimizer.zero_grad()
            critic_loss.backward()
            self.critic_optimizer.step()


class ActorNetwork(nn.Module):
    """Policy network"""
    
    def __init__(self, state_dim, action_dim):
        super().__init__()
        
        self.network = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
        )
        
        self.mean = nn.Linear(128, action_dim)
        self.log_std = nn.Linear(128, action_dim)
    
    def forward(self, state):
        features = self.network(state)
        
        mean = torch.softmax(self.mean(features), dim=-1)
        log_std = self.log_std(features)
        std = torch.exp(log_std.clamp(-20, 2))
        
        return torch.distributions.Normal(mean, std)


class CriticNetwork(nn.Module):
    """Value network"""
    
    def __init__(self, state_dim):
        super().__init__()
        
        self.network = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )
    
    def forward(self, state):
        return self.network(state)
```

## Risk Management

```python
class RiskManager:
    """Portfolio risk management"""
    
    def __init__(self, max_drawdown=0.15, var_limit=0.05):
        self.max_drawdown = max_drawdown
        self.var_limit = var_limit
        self.peak_value = 0
    
    def check_drawdown(self, portfolio_value):
        """Check if drawdown exceeds limit"""
        self.peak_value = max(self.peak_value, portfolio_value)
        
        drawdown = (self.peak_value - portfolio_value) / self.peak_value
        
        if drawdown > self.max_drawdown:
            return True, drawdown
        
        return False, drawdown
    
    def calculate_var(self, returns, confidence=0.95):
        """Value at Risk"""
        return np.percentile(returns, (1 - confidence) * 100)
    
    def calculate_cvar(self, returns, confidence=0.95):
        """Conditional Value at Risk (Expected Shortfall)"""
        var = self.calculate_var(returns, confidence)
        return returns[returns <= var].mean()
    
    def position_sizing(self, volatility, target_vol=0.15):
        """Volatility targeting"""
        return target_vol / volatility
    
    def stop_loss(self, entry_price, current_price, threshold=0.05):
        """Stop loss check"""
        loss = (entry_price - current_price) / entry_price
        return loss > threshold
```

## Evaluation

```python
class Backtest:
    """Backtesting framework"""
    
    def __init__(self, agent, data):
        self.agent = agent
        self.data = data
    
    def run(self):
        """Run backtest"""
        env = PortfolioEnv(self.data)
        state = env.reset()
        
        portfolio_values = [env.portfolio_value]
        weights_history = [env.weights.copy()]
        
        done = False
        while not done:
            action, _ = self.agent.select_action(state)
            state, reward, done, _ = env.step(action)
            
            portfolio_values.append(env.portfolio_value)
            weights_history.append(env.weights.copy())
        
        return {
            'portfolio_values': np.array(portfolio_values),
            'weights': np.array(weights_history),
            'metrics': self.calculate_metrics(portfolio_values)
        }
    
    def calculate_metrics(self, portfolio_values):
        """Calculate performance metrics"""
        returns = np.diff(portfolio_values) / portfolio_values[:-1]
        
        total_return = (portfolio_values[-1] / portfolio_values[0]) - 1
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1
        annual_vol = np.std(returns) * np.sqrt(252)
        sharpe = annual_return / annual_vol if annual_vol > 0 else 0
        
        # Maximum drawdown
        peak = np.maximum.accumulate(portfolio_values)
        drawdown = (peak - portfolio_values) / peak
        max_drawdown = np.max(drawdown)
        
        # Calmar ratio
        calmar = annual_return / max_drawdown if max_drawdown > 0 else 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar
        }
```

## Deliverables

1. **RL Environment**: Implementation
2. **Trained Agent**: PPO/SAC/TD3
3. **Backtest Results**: 2024–2025
4. **Comparison**: vs. benchmarks
5. **Risk Analysis**: Drawdown, VaR, CVaR

## Project Structure

```
AIDS-4_AutoTrader/
├── README.md
├── environment/
│   └── portfolio_env.py
├── agents/
│   ├── ppo.py
│   ├── sac.py
│   └── td3.py
├── risk/
│   └── risk_manager.py
├── evaluation/
│   └── backtest.py
├── data/
│   └── market_data.csv
├── train.py
└── solution_template.py
```

## Tips

1. State representation is crucial - include enough features
2. Reward function design determines behavior
3. Transaction costs matter - penalize turnover
4. Risk management prevents catastrophic losses
5. Compare against simple baselines (equal weight, 60/40)
