//
//  GUIDState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

#import "BaseState.h"

@interface GUIDState : BaseState <State>
{
	NSInteger state;
	NSNumber *fileId;
}

@end
