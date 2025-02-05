import {
  Controller,
  Post,
  Body,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { OrdersService } from './orders.service';
import { CreateOrderDto } from './dto/create-order.dto';

@Controller('orders')
export class OrdersController {
  constructor(private readonly ordersService: OrdersService) {}

  @Post()
  async createOrder(@Body() createOrderDto: CreateOrderDto) {
    try {
      const order = await this.ordersService.createOrder(createOrderDto);
      return { status: 'success', data: order };
    } catch (error) {
      throw new HttpException(
        {
          status: 'error',
          message: 'Failed to Create Order',
          error: error.message,
        },
        HttpStatus.BAD_REQUEST,
      );
    }
  }
}
