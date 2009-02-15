//
//  CheckView.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "CheckView.h"

@implementation CheckView

- (void)touchesEnded:(NSSet *)touches withEvent:(UIEvent *)event
{
	[target performSelector:action];
}

- (void)setTarget:(id)theTarget action:(SEL)theAction
{
	target = theTarget;
	action = theAction;
}

@end
