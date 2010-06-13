//
//  StringChoiceAlert.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>

#import "AlertPrompt.h"

@interface StringChoiceAlert : AlertPrompt
{
	id target;
	SEL action;
}

- initWithPlaceholder:(NSString *)placeholder text:(NSString *)text target:(id)target action:(SEL)action;

@end
