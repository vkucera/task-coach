//
//  AlertPrompt.h
//  Prompt
//
//  Created by Jeff LaMarche on 2/26/09.

#import <Foundation/Foundation.h>

@interface AlertPrompt : UIAlertView <UIAlertViewDelegate>
{
    UITextField *textField;
    void (^cancelAction)(void);
    void (^confirmAction)(NSString *);
}

- (id)initWithTitle:(NSString *)title message:(NSString *)message cancelAction:(void (^)(void))cancelAction confirmAction:(void (^)(NSString *))confirmAction secure:(BOOL)secure;

@end
