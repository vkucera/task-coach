//
//  Items.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 30/08/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "Items.h"

@implementation BaseItem

- init
{
	if ((self = [super init]))
	{
		[self start];
	}
	
	return self;
}

- (void)dealloc
{
	[myValue release];
	
	[super dealloc];
}

- (NSObject *)value
{
	return myValue;
}

- (void)start
{
	state = 0;
	[myValue release];
	myValue = nil;
}

- (NSNumber *)expect
{
	return nil;
}

- (void)feed:(NSData *)data
{
}

- (void)packValue:(NSObject *)value inData:(NSMutableData *)data
{
}

@end

//===================================================================

@implementation IntegerItem

- (NSNumber *)expect
{
	switch (state)
	{
		case 0:
			return [NSNumber numberWithInt:4];
	}

	return nil;
}

- (void)feed:(NSData *)data
{
	assert([data length] == 4);
	
	[myValue release];
	myValue = [[NSNumber numberWithInt:ntohl(*((int *)[data bytes]))] retain];

	state = 1;
}

- (void)packValue:(NSObject *)value inData:(NSMutableData *)data
{
	assert([value isKindOfClass:[NSNumber class]]);
	
	int v = htonl([(NSNumber *)value intValue]);
	[data appendBytes:(const void *)&v length:4];
}

@end

//===================================================================

@implementation StringItem

- (NSNumber *)expect
{
	switch (state)
	{
		case 0:
			return [NSNumber numberWithInt:4];
		case 1:
			return [NSNumber numberWithInt:length];
	}
	
	return nil;
}

- (void)feed:(NSData *)data
{
	switch (state)
	{
		case 0:
			length = ntohl(*((int *)[data bytes]));
			state = 1;
			break;
		case 1:
		{
			char *buffer = (char *)malloc(length + 1);
			memcpy(buffer, [data bytes], length);
			buffer[length] = 0;

			[myValue release];
			myValue = [[NSString stringWithUTF8String:buffer] retain];
			
			free(buffer);
			
			state = 2;
			break;
		}
	}
}

- (void)packValue:(NSObject *)value inData:(NSMutableData *)data
{
	assert((value == nil) || [value isKindOfClass:[NSString class]]);
	
	if (value)
	{
		const char *bf = [(NSString *)value UTF8String];

		int v = htonl(strlen(bf));
		[data appendBytes:(const void *)&v length:4];
		[data appendBytes:bf length:strlen(bf)];
	}
	else
	{
		int v = 0;
		[data appendBytes:(const void *)&v length:4];
	}
}

@end

//===================================================================

@implementation DataItem

- initWithCount:(NSInteger)theCount
{
	if ((self = [super init]))
	{
		count = theCount;
	}
	
	return self;
}

- (NSNumber *)expect
{
	switch (state)
	{
		case 0:
			return [NSNumber numberWithInt:count];
	}
	
	return nil;
}

- (void)feed:(NSData *)data
{
	switch (state)
	{
		case 0:
			[myValue release];
			myValue = [data copy];
			
			state = 1;
			
			break;
	}
}

- (void)packValue:(NSObject *)value inData:(NSMutableData *)data
{
	assert([value isKindOfClass:[NSData class]]);
	
	[data appendData:(NSData *)value];
}

@end


//===================================================================

@implementation VariableDataItem

- (NSNumber *)expect
{
	switch (state)
	{
		case 0:
			return [NSNumber numberWithInt:4];
		case 1:
			return [NSNumber numberWithInt:length];
	}
	
	return nil;
}

- (void)feed:(NSData *)data
{
	switch (state)
	{
		case 0:
			length = ntohl(*((int *)[data bytes]));
			state = 1;
			break;
		case 1:
		{
			[myValue release];
			myValue = [data copy];
			
			state = 2;
			break;
		}
	}
}

- (void)packValue:(NSObject *)value inData:(NSMutableData *)data
{
	assert([value isKindOfClass:[NSData class]]);
	NSData *myData = (NSData *)value;

	int v = htonl([myData length]);
	[data appendBytes:(const void *)&v length:4];
	[data appendData:myData];
}

@end

//===================================================================

@implementation FixedSizeStringItem

- (void)feed:(NSData *)data
{
	[super feed:data];
	
	if (state == 2)
	{
		if ([(NSString *)myValue length] == 0)
		{
			[myValue release];
			myValue = nil;
		}
	}
}

- (void)packValue:(NSObject *)value inData:(NSMutableData *)data
{
	if (value)
	{
		[super packValue:value inData:data];
	}
	else
	{
		int v = 0;
		
		[data appendBytes:(const void *)&v length:4];
	}
}

@end

//===================================================================

@implementation DateItem

- init
{
	if ((self = [super init]))
	{
		fmt = [[NSDateFormatter alloc] init];
		[fmt setDateFormat:@"yyyy-MM-dd"];
	}
	
	return self;
}

- (void)dealloc
{
	[fmt release];
	
	[super dealloc];
}

- (void)feed:(NSData *)data
{
	[super feed:data];
	
	if (state == 2)
	{
		if (myValue)
		{
			NSDate *date = [fmt dateFromString:(NSString *)myValue];
			[myValue release];
			myValue = [date retain];
		}
	}
}

- (void)packValue:(NSObject *)value inData:(NSMutableData *)data
{
	assert((value == nil) || [value isKindOfClass:[NSDate class]]);

	if (value)
	{
		[super packValue:[fmt stringFromDate:(NSDate *)value] inData:data];
	}
	else
	{
		[super packValue:nil inData:data];
	}
}

@end

//===================================================================

@implementation CompositeItem

- initWithItems:(NSArray *)items
{
	if ((self = [super init]))
	{
		myItems = [[NSMutableArray alloc] initWithArray:items];
	}
	
	return self;
}

- (void)dealloc
{
	[myItems release];

	[super dealloc];
}

- (void)append:(BaseItem *)item
{
	[myItems addObject:item];
}

- (void)start
{
	[super start];
	
	[myValue release];
	myValue = (NSObject *)[[NSMutableArray alloc] initWithCapacity:[myItems count]];
	
	for (BaseItem *item in myItems)
		[item start];
}

- (NSNumber *)expect
{
	if (state < [myItems count])
	{
		NSNumber *expect = [(BaseItem *)[myItems objectAtIndex:state] expect];
		
		if (!expect)
		{
			NSObject *value = [(BaseItem *)[myItems objectAtIndex:state] value];

			if (value)
				[(NSMutableArray *)myValue addObject:value];
			else
				[(NSMutableArray *)myValue addObject:[NSNull null]];

			++state;
			
			return [self expect];
		}
		
		return expect;
	}
	else
	{
		return nil;
	}
}

- (void)feed:(NSData *)data
{
	[(BaseItem *)[myItems objectAtIndex:state] feed:data];
}

- (void)packValue:(NSObject *)value inData:(NSMutableData *)data
{
	assert([value isKindOfClass:[NSArray class]]);
	
	int i = 0;
	
	for (BaseItem *item in myItems)
	{
		NSObject *v = [(NSArray *)value objectAtIndex:i];
		
		if (v == [NSNull null])
			[item packValue:nil inData:data];
		else
			[item packValue:v inData:data];

		++i;
	}
}

@end

//===================================================================

@implementation ListItem

- initWithItem:(BaseItem *)item
{
	if ((self = [super init]))
	{
		myItem = [item retain];
	}
	
	return self;
}

- (void)dealloc
{
	[myItem release];

	[super dealloc];
}

- (void)append:(BaseItem *)item
{
	assert([myItem respondsToSelector:@selector(append:)]);

	[myItem performSelector:@selector(append:) withObject:item];
}

- (void)start
{
	[super start];
	
	[myValue release];
	myValue = [[NSMutableArray alloc] init];
	
	[myItem start];
}

- (NSNumber *)expect
{
	switch (state)
	{
		case 0:
			return [NSNumber numberWithInt:4];
		case 1:
		{
			NSNumber *expect = [myItem expect];
			
			if (!expect)
			{
				if (myItem.value)
				{
					[(NSMutableArray *)myValue addObject:[(NSArray *)myItem.value objectAtIndex:0]];
				}
				else
				{
					[(NSMutableArray *)myValue addObject:[NSNull null]];
				}

				--count;
				
				if (!count)
					return nil;
				
				[myItem start];
				return [self expect];
			}
			
			return expect;
		}
	}
	
	return nil;
}

- (void)feed:(NSData *)data
{
	switch (state)
	{
		case 0:
			count = ntohl(*((int *)[data bytes]));
			
			if (count)
			{
				[myItem start];
				state = 1;
			}
			else
				state = 2;
			
			break;
		case 1:
			[myItem feed:data];
			break;
	}
}

- (void)packValue:(NSObject *)value inData:(NSMutableData *)data
{
	assert([value isKindOfClass:[NSArray class]]);

	int v = htonl([(NSMutableArray *)myValue count]);
	[data appendBytes:(const void *)&v length:4];

	for (NSObject *val in (NSMutableArray *)myValue)
	{
		if (val == [NSNull null])
		{
			[myItem packValue:nil inData:data];
		}
		else
		{
			[myItem packValue:val inData:data];
		}
	}
}

@end
