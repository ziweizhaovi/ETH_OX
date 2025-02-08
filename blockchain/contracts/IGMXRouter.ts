export interface IGMXRouter {
  // Core trading functions
  createIncreasePosition(
    path: string[],
    indexToken: string,
    amountIn: bigint,
    minOut: bigint,
    sizeDelta: bigint,
    isLong: boolean,
    acceptablePrice: bigint,
    executionFee: bigint,
    referralCode: string,
    callbackTarget: string
  ): Promise<string>;

  createDecreasePosition(
    path: string[],
    indexToken: string,
    collateralDelta: bigint,
    sizeDelta: bigint,
    isLong: boolean,
    receiver: string,
    acceptablePrice: bigint,
    executionFee: bigint,
    callbackTarget: string
  ): Promise<string>;

  // View functions
  getPositionFee(
    sizeDelta: bigint,
    params: {
      isLong: boolean;
      isIncrease: boolean;
      indexToken: string;
    }
  ): Promise<bigint>;

  getLiquidationPrice(
    account: string,
    collateralToken: string,
    indexToken: string,
    isLong: boolean,
    size: bigint,
    collateral: bigint
  ): Promise<bigint>;
} 