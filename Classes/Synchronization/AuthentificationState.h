//
//  AuthentificationState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

#import "BaseState.h"
#import "KeychainWrapper.h"

@interface AuthentificationState : BaseState <State, UITextFieldDelegate>
{
	NSString *currentPassword;

#if !TARGET_IPHONE_SIMULATOR
	KeychainWrapper *keychain;
#endif
}

@end
