import { Test, TestingModule } from '@nestjs/testing';
import { OrdersController } from './orders.controller';
import { OrdersService } from './orders.service';

describe('OrdersController', () => {
  let controller: OrdersController;
  let service: OrdersService;

  beforeEach(async () => {
    const mockOrdersService = {
      createOrder: jest.fn().mockResolvedValue({
        id: 1,
        customerName: 'Arif Troena',
        product: 'Laptop',
        amount: 2,
      }),
    };

    const module: TestingModule = await Test.createTestingModule({
      controllers: [OrdersController],
      providers: [{ provide: OrdersService, useValue: mockOrdersService }],
    }).compile();

    controller = module.get<OrdersController>(OrdersController);
    service = module.get<OrdersService>(OrdersService);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });

  it('should create an order', async () => {
    const result = await controller.createOrder({
      customerName: 'Arif Troena',
      product: 'Laptop',
      amount: 2,
    });
    expect(result).toEqual({
      status: 'success',
      data: {
        id: 1,
        customerName: 'Arif Troena',
        product: 'Laptop',
        amount: 2,
      },
    });
  });
});
