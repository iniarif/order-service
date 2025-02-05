import { IsString, IsInt, Min, Max, Length } from 'class-validator';

export class CreateOrderDto {
  @IsString()
  @Length(3, 50)
  readonly customerName: string;

  @IsString()
  @Length(2, 100)
  readonly product: string;

  @IsInt()
  @Min(1)
  @Max(1000000000)
  readonly amount: number;
}
