//
//  EndState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

#import "BaseState.h"

@interface EndState : BaseState <State>
{
	BOOL isOK;
}

@end
