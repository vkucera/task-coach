//
//  FullFromDeviceState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 29/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "BaseState.h"

@interface FullFromDeviceState : BaseState <State>
{
	NSMutableArray *categoryIds;
	NSInteger state;
	NSInteger categoryCount;
	NSInteger count;
	NSInteger total;
}

@end
