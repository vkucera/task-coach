//
//  OneShotItemState.m
//  iLibrary
//
//  Created by Jérôme Laheurte on 04/10/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "OneShotItemState.h"
#import "Network.h"

@implementation OneShotItemState

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	[item feed:data];
	
	NSNumber *expect = [item expect];
	if (expect)
	{
		[myNetwork expect:[expect intValue]];
	}
	else
	{
		NSObject *value = [item.value retain];
		
		[self onNewObject:(NSArray *)value];

		[value release];
	}
}

@end
