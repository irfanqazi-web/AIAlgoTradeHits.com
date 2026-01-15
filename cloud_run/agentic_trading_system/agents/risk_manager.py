"""
Risk Management Agent
Monitors and manages trading risk, position sizing, and portfolio exposure
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent, AgentPriority

logger = logging.getLogger(__name__)


class RiskManagerAgent(BaseAgent):
    """
    Risk Management Agent - Monitors and controls trading risk

    Capabilities:
    - Position sizing calculation
    - Stop loss and take profit levels
    - Portfolio risk assessment
    - Exposure monitoring
    - Drawdown tracking
    - Risk/reward analysis
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        default_config = {
            'max_position_size_pct': 5.0,       # Max 5% of portfolio per position
            'max_portfolio_risk_pct': 2.0,      # Max 2% portfolio risk per trade
            'max_total_exposure_pct': 80.0,     # Max 80% total exposure
            'max_sector_exposure_pct': 25.0,    # Max 25% per sector
            'max_correlation_exposure': 0.7,    # Max correlation between positions
            'default_stop_loss_pct': 2.0,       # Default 2% stop loss
            'default_take_profit_pct': 6.0,     # Default 6% take profit (3:1 R/R)
            'max_drawdown_threshold': 10.0,     # Alert if drawdown exceeds 10%
            'volatility_adjustment': True,      # Adjust position size for volatility
            'atr_multiplier_stop': 2.0,         # ATR multiplier for stop loss
            'atr_multiplier_target': 4.0        # ATR multiplier for take profit
        }

        merged_config = {**default_config, **(config or {})}

        super().__init__(
            agent_id=agent_id,
            name="RiskManager",
            description="Monitors and manages trading risk and position sizing",
            config=merged_config
        )

        self.risk_alerts: List[Dict[str, Any]] = []
        self.position_history: List[Dict[str, Any]] = []

    def calculate_position_size(
        self,
        portfolio_value: float,
        entry_price: float,
        stop_loss_price: float,
        risk_per_trade_pct: Optional[float] = None
    ) -> Dict[str, Any]:
        """Calculate optimal position size based on risk parameters"""

        risk_pct = risk_per_trade_pct or self.config['max_portfolio_risk_pct']
        max_position_pct = self.config['max_position_size_pct']

        # Risk amount in dollars
        risk_amount = portfolio_value * (risk_pct / 100)

        # Risk per share
        risk_per_share = abs(entry_price - stop_loss_price)

        if risk_per_share <= 0:
            return {'error': 'Invalid stop loss - must be different from entry price'}

        # Position size based on risk
        shares_by_risk = int(risk_amount / risk_per_share)

        # Position size based on max allocation
        max_position_value = portfolio_value * (max_position_pct / 100)
        shares_by_allocation = int(max_position_value / entry_price)

        # Use the smaller of the two
        optimal_shares = min(shares_by_risk, shares_by_allocation)
        position_value = optimal_shares * entry_price

        return {
            'optimal_shares': optimal_shares,
            'position_value': position_value,
            'position_pct': (position_value / portfolio_value) * 100,
            'risk_amount': optimal_shares * risk_per_share,
            'risk_pct': (optimal_shares * risk_per_share / portfolio_value) * 100,
            'entry_price': entry_price,
            'stop_loss_price': stop_loss_price,
            'risk_per_share': risk_per_share,
            'shares_by_risk': shares_by_risk,
            'shares_by_allocation': shares_by_allocation
        }

    def calculate_stop_levels(
        self,
        entry_price: float,
        atr: Optional[float] = None,
        direction: str = 'long'
    ) -> Dict[str, Any]:
        """Calculate stop loss and take profit levels"""

        if atr and self.config['volatility_adjustment']:
            # ATR-based stops
            stop_distance = atr * self.config['atr_multiplier_stop']
            target_distance = atr * self.config['atr_multiplier_target']
        else:
            # Percentage-based stops
            stop_distance = entry_price * (self.config['default_stop_loss_pct'] / 100)
            target_distance = entry_price * (self.config['default_take_profit_pct'] / 100)

        if direction == 'long':
            stop_loss = entry_price - stop_distance
            take_profit = entry_price + target_distance
        else:  # short
            stop_loss = entry_price + stop_distance
            take_profit = entry_price - target_distance

        risk_reward_ratio = target_distance / stop_distance if stop_distance > 0 else 0

        return {
            'entry_price': entry_price,
            'direction': direction,
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'stop_distance': stop_distance,
            'target_distance': target_distance,
            'stop_pct': (stop_distance / entry_price) * 100,
            'target_pct': (target_distance / entry_price) * 100,
            'risk_reward_ratio': round(risk_reward_ratio, 2),
            'atr_used': atr
        }

    def assess_trade_risk(
        self,
        signal: Dict[str, Any],
        portfolio_value: float = 100000
    ) -> Dict[str, Any]:
        """Assess the risk of a potential trade"""

        symbol = signal.get('symbol')
        price = signal.get('price')
        confidence = signal.get('confidence', 0)
        direction = signal.get('direction', 'long')

        if not price:
            return {'error': 'No price data', 'approved': False}

        # Get market data for volatility
        data = self.get_market_data(symbol, 'stocks', 'daily', limit=20)
        atr = data[0].get('atr') if data else None

        # Calculate stop levels
        stop_levels = self.calculate_stop_levels(price, atr, direction)

        # Calculate position size
        position = self.calculate_position_size(
            portfolio_value,
            price,
            stop_levels['stop_loss']
        )

        # Risk assessment
        risk_score = 0
        risk_factors = []

        # Check confidence level
        if confidence < 0.6:
            risk_score += 2
            risk_factors.append(f'Low confidence: {confidence:.1%}')
        elif confidence < 0.7:
            risk_score += 1
            risk_factors.append(f'Moderate confidence: {confidence:.1%}')

        # Check risk/reward ratio
        if stop_levels['risk_reward_ratio'] < 2:
            risk_score += 2
            risk_factors.append(f'Low R/R ratio: {stop_levels["risk_reward_ratio"]}')

        # Check position size
        if position.get('position_pct', 0) > self.config['max_position_size_pct']:
            risk_score += 3
            risk_factors.append(f'Position too large: {position["position_pct"]:.1f}%')

        # Check volatility (if ATR available)
        if atr and data:
            volatility_pct = (atr / price) * 100
            if volatility_pct > 5:
                risk_score += 2
                risk_factors.append(f'High volatility: {volatility_pct:.1f}%')

        # Risk level classification
        if risk_score <= 2:
            risk_level = 'LOW'
            approved = True
        elif risk_score <= 4:
            risk_level = 'MEDIUM'
            approved = True
        elif risk_score <= 6:
            risk_level = 'HIGH'
            approved = confidence >= 0.7
        else:
            risk_level = 'EXTREME'
            approved = False

        assessment = {
            'symbol': symbol,
            'price': price,
            'direction': direction,
            'confidence': confidence,
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'approved': approved,
            'stop_levels': stop_levels,
            'position_sizing': position,
            'assessed_at': datetime.utcnow().isoformat()
        }

        if not approved:
            self.risk_alerts.append({
                'type': 'trade_rejected',
                'symbol': symbol,
                'reason': risk_factors,
                'timestamp': datetime.utcnow().isoformat()
            })

        return assessment

    def monitor_portfolio_risk(
        self,
        positions: List[Dict[str, Any]],
        portfolio_value: float
    ) -> Dict[str, Any]:
        """Monitor overall portfolio risk"""

        if not positions:
            return {
                'total_exposure': 0,
                'exposure_pct': 0,
                'risk_level': 'NONE',
                'alerts': []
            }

        total_exposure = sum(p.get('value', 0) for p in positions)
        exposure_pct = (total_exposure / portfolio_value) * 100

        # Sector exposure
        sector_exposure = {}
        for pos in positions:
            sector = pos.get('sector', 'Unknown')
            sector_exposure[sector] = sector_exposure.get(sector, 0) + pos.get('value', 0)

        alerts = []

        # Check total exposure
        if exposure_pct > self.config['max_total_exposure_pct']:
            alerts.append({
                'type': 'HIGH_EXPOSURE',
                'message': f'Total exposure {exposure_pct:.1f}% exceeds {self.config["max_total_exposure_pct"]}%',
                'severity': 'HIGH'
            })

        # Check sector concentration
        for sector, value in sector_exposure.items():
            sector_pct = (value / portfolio_value) * 100
            if sector_pct > self.config['max_sector_exposure_pct']:
                alerts.append({
                    'type': 'SECTOR_CONCENTRATION',
                    'message': f'{sector} exposure {sector_pct:.1f}% exceeds {self.config["max_sector_exposure_pct"]}%',
                    'severity': 'MEDIUM'
                })

        # Determine risk level
        if len(alerts) == 0:
            risk_level = 'LOW'
        elif any(a['severity'] == 'HIGH' for a in alerts):
            risk_level = 'HIGH'
        else:
            risk_level = 'MEDIUM'

        return {
            'total_exposure': total_exposure,
            'exposure_pct': exposure_pct,
            'sector_exposure': sector_exposure,
            'position_count': len(positions),
            'risk_level': risk_level,
            'alerts': alerts,
            'checked_at': datetime.utcnow().isoformat()
        }

    def handle_message(self, message) -> Dict[str, Any]:
        """Handle incoming messages"""
        msg_type = message.message_type

        if msg_type == 'assess_trade':
            signal = message.payload.get('signal', {})
            portfolio_value = message.payload.get('portfolio_value', 100000)
            return self.assess_trade_risk(signal, portfolio_value)

        elif msg_type == 'calculate_position':
            return self.calculate_position_size(
                message.payload.get('portfolio_value', 100000),
                message.payload.get('entry_price'),
                message.payload.get('stop_loss_price')
            )

        elif msg_type == 'portfolio_check':
            positions = message.payload.get('positions', [])
            portfolio_value = message.payload.get('portfolio_value', 100000)
            return self.monitor_portfolio_risk(positions, portfolio_value)

        return super().handle_message(message)

    def execute(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute risk management checks"""
        context = context or {}

        signals = context.get('signals', [])
        portfolio_value = context.get('portfolio_value', 100000)
        positions = context.get('positions', [])

        # Assess all signals
        assessments = []
        for signal in signals:
            if signal.get('signal_type') in ['buy', 'sell']:
                assessment = self.assess_trade_risk(signal, portfolio_value)
                assessments.append(assessment)

        # Monitor portfolio
        portfolio_risk = self.monitor_portfolio_risk(positions, portfolio_value)

        # Filter approved trades
        approved_trades = [a for a in assessments if a.get('approved')]
        rejected_trades = [a for a in assessments if not a.get('approved')]

        self.log_execution('risk_assessment', {
            'signals_assessed': len(assessments),
            'approved': len(approved_trades),
            'rejected': len(rejected_trades),
            'portfolio_risk_level': portfolio_risk['risk_level']
        })

        return {
            'assessments': assessments,
            'approved_trades': approved_trades,
            'rejected_trades': rejected_trades,
            'portfolio_risk': portfolio_risk,
            'risk_alerts': self.risk_alerts[-10:]  # Last 10 alerts
        }
